# Импортировать стандартные модули, используемые в этой игре
# Модуль экрана не импортируется, потому что он передается как объект в вызываемую функцию
from time import sleep
from random import randrange
from machine import Pin

# Функция, которая возвращает название вашей игры
def get_game_name():
    game_name = "Button Cowboys"
    return game_name

# Основная функция игры, которая вызывается в главном меню тетриса
def game_loop(oled, led_user_1, led_user_2):
    
    # Определить пины кнопок, которые будут использоваться в этой игре и обрабатываться на первом ядре
    down = Pin(27, Pin.IN, Pin.PULL_UP)
    action_b = Pin(4, Pin.IN, Pin.PULL_UP)
    
    # Игровой цикл, который выполняется бесконечно, пока не будет вызвано условие сброса из второго ядра
    while(True):
        
        # Очистить экран и установить переменную для цикла while
        oled.fill(0)
        oled.show()
        go_on = True
        
        # Нарисовать инструкции для игры и подождать 3 секунды
        oled.text("PL1 - B", 0, 0, 1)
        oled.text("PL2 - DOWN", 0, 10, 1)
        oled.line(0, 19, 127, 19, 1)
        oled.text("first one to", 0, 21, 1)
        oled.text("press button", 0, 30, 1)
        oled.text("after 'GO' wins", 0, 39, 1)
        oled.show()
        sleep(3)
        
        # Очистить экран и подождать случайное время перед противостоянием
        oled.fill(0)
        oled.text("get ready...", 16, 29, 1) 
        oled.show()
        sleep(randrange(3, 15, 1))
        
        # "Высокий полдень" и запомнить состояние кнопки, чтобы человек, удерживающий кнопку, не выигрывал автоматически
        oled.fill(1)
        oled.text("GO", 56, 29, 0)
        previous_down_state = down.value()
        previous_b_state = action_b.value()
        oled.show()
        
        # Проверить изменение состояния кнопки, выйти из цикла while и назначить победителя соответствующим образом
        while (go_on):
            if (previous_b_state != action_b.value()):
                led_user_2.value(1)
                oled.fill(0)
                oled.text("PLAYER 1 WINS", 12, 29, 1)
                go_on = False
            if (previous_down_state != down.value()):
                led_user_1.value(1)
                oled.fill(0)
                oled.text("PLAYER 2 WINS", 12, 29, 1)
                go_on = False
                
        # Показать имя победившего игрока и выключить светодиоды перед перезапуском игры
        oled.show()
        sleep(3)
        oled.fill(0)
        oled.show()
        led_user_1.value(0)
        led_user_2.value(0)