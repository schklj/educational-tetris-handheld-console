# function that returns the name of your game 
def get_game_name():
    game_name = "Your Game"
    return game_name

# main function of the game that is called in the main menu of the tetris
def game_loop(oled):
    oled.fill(0)
    oled.show()
    
    # infinite loop that does nothing
    while (True):
        pass