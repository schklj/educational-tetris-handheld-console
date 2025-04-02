# Импортировать стандартные модули, используемые в этой игре
# Модуль экрана не импортируется, потому что он передается как объект в вызываемую функцию
from time import sleep
from random import randint
from machine import Pin

# Функция, которая возвращает название вашей игры
def get_game_name():
    game_name = "2P Pong"
    return game_name

# Основная функция игры, которая вызывается в главном меню тетриса
def game_loop(oled, led_user_1, led_user_2):
    
    # Определить пины кнопок, которые будут использоваться в этой игре и обрабатываться на втором ядра
    up = Pin(15, Pin.IN, Pin.PULL_UP)
    down = Pin(27, Pin.IN, Pin.PULL_UP)
    action_a = Pin(5, Pin.IN, Pin.PULL_UP)
    action_b = Pin(4, Pin.IN, Pin.PULL_UP)
    
    # Игровой цикл, который выполняется бесконечно, пока не будет вызвано условие сброса
    while (True):
        
        # Хардкодированные значения начальных позиций ракетки
        paddle_1_coord = 27
        paddle_2_coord = 27
    
        # Хардкодированные значения начальной позиции и скорости "мяча"
        x_coord = 62
        y_coord = 30
        x_speed = 2
        y_speed = 1
        
        # Случайным образом назначить направление мяча в начале игры
        if (randint(0, 1) == 0):
            x_speed = x_speed * -1
        if (randint(0, 1) == 0):
            y_speed = y_speed * -1
    
        # Установить в false, когда мяч покидает игровое поле
        game_continue_condition = True
        
        # Хранит номер игрока, который победил
        winner = 0
    
        # Продолжать игру, пока мяч находится на игровом поле
        while (game_continue_condition):
            
            # Нарисовать ракетки и мяч в соответствии с их координатами
            oled.fill(0)
            oled.fill_rect(x_coord, y_coord, 4, 4, 1)
            oled.fill_rect(0, paddle_1_coord, 4, 10, 1)
            oled.fill_rect(124, paddle_2_coord, 4, 10, 1)
            oled.show()
    
            # Изменить координаты мяча на значение скорости
            x_coord = x_coord + x_speed
            y_coord = y_coord + y_speed
        
            # Инвертировать значение скорости мяча при столкновении с ракеткой, чтобы он отразился
            if ((x_coord > 120) and (y_coord + 2 >= paddle_2_coord) and (y_coord + 2 <= paddle_2_coord + 10)):
                x_speed = x_speed * -1
            if ((x_coord < 8) and (y_coord + 2 >= paddle_1_coord) and (y_coord + 2 <= paddle_1_coord + 10)):
                x_speed = x_speed * -1
            
            # Инвертировать значение скорости мяча при столкновении с потолком и полом, чтобы он отразился
            if (y_coord > 58):
                y_speed = y_speed * -1
            if (y_coord < 1):
                y_speed = y_speed * -1
            
            # Если мяч проходит мимо ракетки, завершить игру и назначить соответствующего победителя
            if (x_coord > 130):
                game_continue_condition = False
                winner = 1
            if (x_coord < -6):
                game_continue_condition = False
                winner = 2
            
            # Изменить координаты ракеток, пока кнопки удерживаются
            if (up.value() == 0):
                if (paddle_2_coord >= 1):
                    paddle_2_coord = paddle_2_coord - 2
            if (down.value() == 0):
                if (paddle_2_coord <= 53):
                    paddle_2_coord = paddle_2_coord + 2
            if (action_a.value() == 0):
                if (paddle_1_coord >= 1):
                    paddle_1_coord = paddle_1_coord - 2
            if (action_b.value() == 0):
                if (paddle_1_coord <= 53):
                    paddle_1_coord = paddle_1_coord + 2
        
        # Очистить экран и нарисовать таблички с плашки победителей, пока не вернемся к началу игры и не перезапустится код игры
        oled.fill(0)
        if (winner == 1):
            oled.text("PLAYER 1", 32, 24, 1)
        if (winner == 2):
            oled.text("PLAYER 2", 32, 24, 1)    
        oled.text("WON", 52, 33, 1)
        oled.show()
        sleep(1)