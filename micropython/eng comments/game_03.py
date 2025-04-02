# function that returns the name of your game 
def get_game_name():
    game_name = "Flashlight"
    return game_name

# main function of the game that is called in the main menu of the tetris
def game_loop(oled, rgb):
    
    # wipe the screen and indenetly send the command the rgb led to lightup white 
    while(True):
        oled.fill(0)
        oled.show()
        rgb[0] = (255, 255, 255)
        rgb.write()