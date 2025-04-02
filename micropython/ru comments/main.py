# Импорт стандартных библиотек
from machine import Pin
from machine import PWM
from machine import I2C
from time import sleep
from time import ticks_ms
from neopixel import NeoPixel
from random import randrange
import _thread

# Импорт библиотеки для "OLED" дисплея
from ssd1306 import SSD1306_I2C

# Импорт пользовательских игровых файлов
import game_01
import game_02
import game_03
import game_04

# Блокировки памяти должны использоваться, когда используются два ядра и они работают с одной и той же памятью
# Однако далее я не буду их использовать
lock = _thread.allocate_lock()

# Определения объектов кнопок (input)
# Плюс глобальные переменные, которые хранят инверсированные значения состояний кнопок
# Эти переменные избыточны, просто более удобный способ чтения состояний кнопок
up = Pin(15, Pin.IN, Pin.PULL_UP)
is_up = False
down = Pin(27, Pin.IN, Pin.PULL_UP)
is_down = False
right = Pin(28, Pin.IN, Pin.PULL_UP)
is_right = False
left = Pin(26, Pin.IN, Pin.PULL_UP)
is_left = False
action_a = Pin(5, Pin.IN, Pin.PULL_UP)
is_a = False
action_b = Pin(4, Pin.IN, Pin.PULL_UP)
is_b = False
mute = Pin(1, Pin.IN, Pin.PULL_UP)
is_mute = False
main_menu = Pin(7, Pin.IN, Pin.PULL_UP)
is_menu = False

# Определения объектов светодиодов (output)
led_mute = Pin(0, Pin.OUT)
led_user_1 = Pin(14, Pin.OUT)
led_user_2 = Pin(6, Pin.OUT)

# Определения объекта АЦП
# Считывание фактического напряжения батареи не работает должным образом с текущей схемой
# Во время разряда батареи напряжение, считываемое АЦП, сначала падает, а затем начинает расти, вызывая проблемы
batt_voltage = machine.ADC(29)
read_voltage = 0

# Определения объектов I2C и дисплея
i2c = I2C(1, sda = Pin(2), scl = Pin(3), freq = 400000)
oled = SSD1306_I2C(128, 64, i2c)

# Определения объектов пищалки (PWM)
buzzer = PWM(8, freq = 440, duty_u16 = 0)
buzzer_is_on = True

# Определения объектов NeoPixel
rgb_led = Pin(16, Pin.OUT)
rgb = NeoPixel(rgb_led, 1)
color_components = [0, 0, 0]

# Последовательность звуков для экрана загрузки
# Выполняется на втором ядре, поэтому используются "sleep"
def loading_screen_tune():
    #C4 нота
    buzzer.freq(262)
    buzzer.duty_u16(32768)
    sleep(0.2)
    buzzer.duty_u16(0)
    sleep(0.1)
    #D4 нота 
    buzzer.freq(294)
    buzzer.duty_u16(32768)
    sleep(0.2)
    buzzer.duty_u16(0)
    sleep(0.1)
    #E4 нота
    buzzer.freq(330)
    buzzer.duty_u16(32768)
    sleep(0.2)
    buzzer.duty_u16(0)
    sleep(0.1)
    

# АБСОЛЮТНО (не)ОБХОДИМЫЙ ЭКРАН ЗАГРУЗКИ
def loading_screen(oled, rgb, led_user_1, led_user_2, buzzer):
    
    # Очистить экран и выключить светодиоды и зуммер на всякий случай
    oled.fill(0)
    oled.show()
    rgb[0] = (0, 0, 0)
    rgb.write()
    led_user_1.value(0)
    led_user_2.value(0)
    buzzer.duty_u16(0)
    
    # Эта функция запускает код на втором ядре
    # В этом случае этот код просто воспроизводит короткую мелодию из трёх нот
    _thread.start_new_thread(loading_screen_tune, ())
    
    # Этот массив содержит слова, которые будут отображаться по порядку в процессе загрузки
    words_to_show = ["TETRIS", "by", "SHKLJ"]
    
    # Итерация по ранее упомянутому массиву и отображение содержимого в центре экрана, каждое на новой строке
    # Именно здесь я отказываюсь от парадигмы обобщённого программирования и просто грубой силой рисую пиксели на экране
    for i in range(len(words_to_show)):
        oled.text(words_to_show[i], 64 - (len(words_to_show[i]) * 4), (i * 9) + 1, 1)
        oled.show()
        sleep(0.3)
        
    # Нарисовать ограничивающий прямоугольник для индикатора прогресса
    oled.line(10,  55, 117, 55, 1)
    oled.line(10,  60, 117, 60, 1)
    oled.line(10,  55, 10,  60, 1)
    oled.line(117, 55, 117, 60, 1)
    oled.show()
    
    # Заполнение шкалы загрузки
    for i in range(12, 116):
        oled.fill_rect(i, 57, 1, 2, 1)
        oled.show()
        
    # Закрасить экран белым
    oled.fill(1)
    oled.show()
    sleep(0.2)
    oled.fill(0)
    oled.show()

# Вызов и выполнение абсолютно (не)обходимого экрана загрузки
# Если вы хотите отключить "экран загрузки", просто закомментируйте эту строку
loading_screen(oled, rgb, led_user_1, led_user_2, buzzer)

# Код второго ядра
# Этот код не является строго необходимым, но отвечает за поведение кнопки отключения звука и кнопки сброса
# На самом RP2040-Zero уже есть кнопка сброса, фактически нет необходимости во второй кнопке, её можно перепрофилировать, как и кнопку отключения звука
# Ещё одна причина отказаться от второго ядра и использовать его для других задач — это то, что при каждой итерации оно отключает зуммер, если кнопка не нажата
# Это делает невозможным воспроизведение звуков на другом ядре
# Но если удалить этот код, то кнопки на главном меню перестанут работать
def second_core(up, right, left, down, action_a, action_b, mute, main_menu, buzzer):
    
    # Определение глобальных переменных, которые будут использоваться в главном меню
    # Глобальные переменные в целом плохая идея в программировании
    # Особенно в многозадачных системах, таких как эта, из-за проблем с доступом к памяти
    global is_up
    global is_down
    global is_left
    global is_right
    global is_a
    global is_b
    global is_mute
    global is_menu
    global buzzer_is_on
    
    # Эта переменная необходима для обнаружения возрастующего фронта нажатия кнопки, чтобы срабатывать один раз, а не всё время
    previous_mute_state = 0
    
    while(True):
        
        # Глупая часть кода, которая просто инвертирует состояние переменной кнопки и сохраняет в другую переменную
        # Снова, если удалить, нарушится работа главного меню, кнопки отключения звука и пользовательской кнопки сброса
        # Инвертирование могло бы быть выполнено на уровне железа, подтягивая входные пины и подключив кнопки к 3.3V
        if (up.value() == False):
            is_up = 1
        else:
            is_up = 0
        if (down.value() == False):
            is_down = 1
        else:
            is_down = 0
        if (right.value() == False):
            is_right = 1
        else:
            is_right = 0
        if (left.value() == False):
            is_left = 1
        else:
            is_left = 0
        if (action_a.value() == False):
            is_a = 1
        else:
            is_a = 0
        if (action_b.value() == False):
            is_b = 1
        else:
            is_b = 0
        if (mute.value() == False):
            is_mute = 1
        else:
            is_mute = 0
        if (main_menu.value() == False):
            is_menu = 1
        else:
            is_menu = 0
            
        # Поведение кнопки отключения звука для возрастающего фронта сиграла с нажатия кнопки
        if (previous_mute_state != is_mute):
            if (is_mute == True):
                if (led_mute.value() == 0):
                    led_mute.value(1)
                    buzzer_is_on = False
                else:
                    led_mute.value(0)
                    buzzer_is_on = True
        previous_mute_state = is_mute

        # Этот код отвечает за воспроизведение звуков при нажатии кнопок
        # Он также отключает все звуки, когда кнопки не нажаты
        # Это делает невозможным воспроизведение звуков на других ядрах, когда этот код активен
        if (buzzer_is_on == False):
            buzzer.duty_u16(0)
        else:
            if (is_up):
                buzzer.duty_u16(32768)
                buzzer.freq(330)
            elif (is_left):
                buzzer.duty_u16(32768)
                buzzer.freq(349)
            elif (is_right):
                buzzer.duty_u16(32768)
                buzzer.freq(440)
            elif (is_down):
                buzzer.duty_u16(32768)
                buzzer.freq(494)
            elif (is_a):
                buzzer.duty_u16(32768)
                buzzer.freq(523)
            elif (is_b):
                buzzer.duty_u16(32768)
                buzzer.freq(659)
            else:
                buzzer.duty_u16(0)
        
        # Этот код перезагружает МК, когда нажата кнопка "main menu"
        # Поскольку к кнопкам не подключены параллельные конденсаторы, иногда игра зависает из-за дребезга контактов
        # Как уже упоминалось, эту кнопку лучше перепрофилировать для другой функции
        # В качестве альтернативы можно реализовать программный таймер для сброса тетриса после длительного нажатия вместо конденсаторов
        if (is_menu):
            machine.reset()

# Запустить код "second_core" на втором ядре
# Второе ядро не может выполнять два потока одновременно, но к этому времени "loading_screen_tune" уже завершён
# Будьте осторожны при изменении временных интервалов последовательности экрана загрузки, так как это может привести к зависанию игры
_thread.start_new_thread(second_core, (up, right, left, down, action_a, action_b, mute, main_menu, buzzer))

# Считывает напряжение батареи один раз при запуске игры и сохраняет в переменную
read_voltage = batt_voltage.read_u16()

# Переменные, необходимые для срабатывания на возрастающий фронт нажатия кнопки в главном меню
previous_up_state = 0
previous_right_state = 0
previous_left_state = 0
previous_down_state = 0
previous_a_state = 0
previous_b_state = 0

# Начать главное меню с первым выделенным элементом
list_hightlight = 1

while (True):
    
    # Нарисовать "main menu" и уровень батареи в верхней и нижней части экрана
    oled.show()
    oled.fill(0)
    oled.text("Main Menu", 28, 0, 1)
    oled.line(0, 8, 127, 8, 1)
    oled.line(0, 54, 127, 54 ,1)
    oled.text("Battery:", 0, 56, 1)
    if (read_voltage > 59000):
        oled.text("FULL", 64, 56, 1)
    elif (read_voltage > 10000 and read_voltage <= 59000):
        oled.text("NOFULL", 64, 56, 1)
    elif (read_voltage <= 10000):
        oled.text("NO", 64, 56, 1)
    
    # Обрабатывать нажатия кнопок для перемещения выделения вверх и вниз с помощью кнопок направления
    if (previous_up_state != is_up):
        if (is_up == True):
            if (list_hightlight == 1):
                list_hightlight = 4
            else:
                list_hightlight = list_hightlight - 1
    previous_up_state = is_up
    if (previous_right_state != is_right):
        if (is_right == True):
            if (list_hightlight == 4):
                list_hightlight = 1
            else:
                list_hightlight = list_hightlight + 1
    previous_right_state = is_right
    if (previous_left_state != is_left):
        if (is_left == True):
            if (list_hightlight == 1):
                list_hightlight = 4
            else:
                list_hightlight = list_hightlight - 1
    previous_left_state = is_left
    if (previous_down_state != is_down):
        if (is_down == True):
            if (list_hightlight == 4):
                list_hightlight = 1
            else:
                list_hightlight = list_hightlight + 1
    previous_down_state = is_down
    
    # Запустить функцию игры после нажатия кнопки действия в зависимости от того, какой элемент был выделен
    if ((previous_a_state != is_a) or (previous_b_state != is_b)):
        if ((is_a == True) or (is_b == True)):
            if (list_hightlight == 1):
                game_01.game_loop(oled, led_user_1, led_user_2)
            elif (list_hightlight == 2):
                game_02.game_loop(oled, led_user_1, led_user_2)
            elif (list_hightlight == 3):
                game_03.game_loop(oled, rgb)
            elif (list_hightlight == 4):
                game_04.game_loop(oled)
    previous_a_state = is_a
    previous_b_state = is_b
    
    # Нарисовать белый прямоугольник в позиции, соответствующей выделенной игре
    oled.fill_rect(0, list_hightlight * 11 - 1, 127, 10, 1)
    
    # Нарисовать названия игр белым цветом, за исключением выделенной игры
    # Всё ещё не уверен, как это работает, но это работает
    oled.text(game_01.get_game_name(), 0, 11, list_hightlight - 1)
    oled.text(game_02.get_game_name(), 0, 22, list_hightlight - 2)
    oled.text(game_03.get_game_name(), 0, 33, list_hightlight - 3)
    oled.text(game_04.get_game_name(), 0, 44, list_hightlight - 4)
    