# Функция, которая возвращает название вашей игры
def get_game_name():
    game_name = "Flashlight"
    return game_name

# Основная функция игры, которая вызывается в главном меню тетриса
def game_loop(oled, rgb):
    
    # Очистить экран и бесконечно отправлять команду для включения белого цвета на RGB-светодиоде 
    while(True):
        oled.fill(0)
        oled.show()
        rgb[0] = (255, 255, 255)
        rgb.write()