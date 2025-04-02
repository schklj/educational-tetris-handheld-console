# import standart modules that are used by this game
# screen module is not imported because it is passed as an object to the called function
from time import sleep
from random import randint
from machine import Pin

# function that returns the name of your game 
def get_game_name():
    game_name = "2P Pong"
    return game_name

# main function of the game that is called in the main menu of the tetris
def game_loop(oled, led_user_1, led_user_2):
    
    # define button pins that will be used by this game and handled on the second core
    up = Pin(15, Pin.IN, Pin.PULL_UP)
    down = Pin(27, Pin.IN, Pin.PULL_UP)
    action_a = Pin(5, Pin.IN, Pin.PULL_UP)
    action_b = Pin(4, Pin.IN, Pin.PULL_UP)
    
    # game loop that runs indefinetely untill the reset condition is called
    while (True):
        
        # hardcoded values of the starting positions of the paddle 
        paddle_1_coord = 27
        paddle_2_coord = 27
    
        # hardcoded values of the starting position and speed of the "ball"
        x_coord = 62
        y_coord = 30
        x_speed = 2
        y_speed = 1
        
        # randomly assign direction of the ball at the start of the game
        if (randint(0, 1) == 0):
            x_speed = x_speed * -1
        if (randint(0, 1) == 0):
            y_speed = y_speed * -1
    
        # set to false when ball leaves the playing field
        game_continue_condition = True
        
        # stores the number of a player that won
        winner = 0
    
        # run the game while the ball in in the playing field
        while (game_continue_condition):
            
            # draw paddles and the ball in accoding their coodrinates
            oled.fill(0)
            oled.fill_rect(x_coord, y_coord, 4, 4, 1)
            oled.fill_rect(0, paddle_1_coord, 4, 10, 1)
            oled.fill_rect(124, paddle_2_coord, 4, 10, 1)
            oled.show()
    
            # change the coordinate of the ball by the speed value
            x_coord = x_coord + x_speed
            y_coord = y_coord + y_speed
        
            # invert the speed value of the ball when it collides with the paddle making it reflect
            if ((x_coord > 120) and (y_coord + 2 >= paddle_2_coord) and (y_coord + 2 <= paddle_2_coord + 10)):
                x_speed = x_speed * -1
            if ((x_coord < 8) and (y_coord + 2 >= paddle_1_coord) and (y_coord + 2 <= paddle_1_coord + 10)):
                x_speed = x_speed * -1
            
            # invert the speed value of the ball when it collides with the ceiling and the floor making it reflect
            if (y_coord > 58):
                y_speed = y_speed * -1
            if (y_coord < 1):
                y_speed = y_speed * -1
            
            # if the ball goes past the paddle make end trhe game and assign the corresponding winner
            if (x_coord > 130):
                game_continue_condition = False
                winner = 1
            if (x_coord < -6):
                game_continue_condition = False
                winner = 2
            
            # change the coordinate of the paddles when buttons are being held
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
        
        # wipe the screen and draw winner nameplates, until returning to the start of the game and restarting the gamecode
        oled.fill(0)
        if (winner == 1):
            oled.text("PLAYER 1", 32, 24, 1)
        if (winner == 2):
            oled.text("PLAYER 2", 32, 24, 1)    
        oled.text("WON", 52, 33, 1)
        oled.show()
        sleep(1)