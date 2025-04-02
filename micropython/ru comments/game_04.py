# Функция, которая возвращает название вашей игры
def get_game_name():
    game_name = "Your Game"
    return game_name

# Основная функция игры, которая вызывается в главном меню тетриса
def game_loop(oled):
    oled.fill(0)
    oled.show()
    
    # Бесконечный цикл, внутри этого цикла нужно написать свою игру
    while (True):
        pass