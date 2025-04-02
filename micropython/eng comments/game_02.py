# import standart modules that are used by this game
# screen module is not imported because it is passed as an object to the called function
from time import sleep
from random import randrange
from machine import Pin

# function that returns the name of your game 
def get_game_name():
    game_name = "Button Cowboys"
    return game_name

# main function of the game that is called in the main menu of the tetris
def game_loop(oled, led_user_1, led_user_2):
    
    # define button pins that will be used by this game and handled on the second core
    down = Pin(27, Pin.IN, Pin.PULL_UP)
    action_b = Pin(4, Pin.IN, Pin.PULL_UP)
    
    # game loop that runs indefinetely untill the reset condition is called
    while(True):
        
        # clean the screen and set a varible for the while loop
        oled.fill(0)
        oled.show()
        go_on = True
        
        # draw instrucions for the game and wait 3 seconds
        oled.text("PL1 - B", 0, 0, 1)
        oled.text("PL2 - DOWN", 0, 10, 1)
        oled.line(0, 19, 127, 19, 1)
        oled.text("first one to", 0, 21, 1)
        oled.text("press button", 0, 30, 1)
        oled.text("after 'GO' wins", 0, 39, 1)
        oled.show()
        sleep(3)
        
        # wipe the screen and wait for a random time before the standoff
        oled.fill(0)
        oled.text("get ready...", 16, 29, 1) 
        oled.show()
        sleep(randrange(3, 15, 1))
        
        # "high noon" and remember the button state so that the person holding down the button doesn't automatically win
        oled.fill(1)
        oled.text("GO", 56, 29, 0)
        previous_down_state = down.value()
        previous_b_state = action_b.value()
        oled.show()
        
        # check the change of state of the button, leave the while loop and assign the winner accordingly
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
                
        # show the name of the winning person and turn off leds until restarting the game
        oled.show()
        sleep(3)
        oled.fill(0)
        oled.show()
        led_user_1.value(0)
        led_user_2.value(0)