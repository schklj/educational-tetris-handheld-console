# import standart libraries 
from machine import Pin
from machine import PWM
from machine import I2C
from time import sleep
from time import ticks_ms
from neopixel import NeoPixel
from random import randrange
import _thread

# import library for the oled display
from ssd1306 import SSD1306_I2C

# import custom game files
import game_01
import game_02
import game_03
import game_04

# memory locks should be used when two cores are used
# however i am not using them onwards
lock = _thread.allocate_lock()

# definitions of button(input) objects
# plus global variables that hold inverted values for button states
# those variables are superfluous, just a nicer way to read button states
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

# definitions of LED(output) objects
led_mute = Pin(0, Pin.OUT)
led_user_1 = Pin(14, Pin.OUT)
led_user_2 = Pin(6, Pin.OUT)

# definitions of ADC object
# reading actual battery voltage doesn't work properly with currect schematic
# during battery discharge voltage read by ADC drops at first, then starts rising, riveting
batt_voltage = machine.ADC(29)
read_voltage = 0

# definitions of i2c and display objects
i2c = I2C(1, sda = Pin(2), scl = Pin(3), freq = 400000)
oled = SSD1306_I2C(128, 64, i2c)

# definitions of buzzer(PMW) objects
buzzer = PWM(8, freq = 440, duty_u16 = 0)
buzzer_is_on = True

# definitions of neopixel objects
rgb_led = Pin(16, Pin.OUT)
rgb = NeoPixel(rgb_led, 1)
color_components = [0, 0, 0]

# sequence of sounds for the loading screen
# executed on the second core, that's why "sleeps" are used
def loading_screen_tune():
    # C4 tone
    buzzer.freq(262)
    buzzer.duty_u16(32768)
    sleep(0.2)
    buzzer.duty_u16(0)
    sleep(0.1)
    # D4 tone 
    buzzer.freq(294)
    buzzer.duty_u16(32768)
    sleep(0.2)
    buzzer.duty_u16(0)
    sleep(0.1)
    # E4 tone
    buzzer.freq(330)
    buzzer.duty_u16(32768)
    sleep(0.2)
    buzzer.duty_u16(0)
    sleep(0.1)
    

# ABSOLUTELY (not) NESSESARY LOADING SCREEN
def loading_screen(oled, rgb, led_user_1, led_user_2, buzzer):
    
    # clean the screen and turn off leds and buzzer just in case
    oled.fill(0)
    oled.show()
    rgb[0] = (0, 0, 0)
    rgb.write()
    led_user_1.value(0)
    led_user_2.value(0)
    buzzer.duty_u16(0)
    
    # this function starts code running on the second core
    # in this case this code just plays a short tune of three notes
    _thread.start_new_thread(loading_screen_tune, ())
    
    # this array holds words that will be displayed in order in the loading sequence
    words_to_show = ["TETRIS", "by", "SHKLJ"]
    
    # iterates over the previously mentioned array and displays contents in the centre of the screen each on the new line
    # precisely here i give up on the generalisation paradigm of programming and just brute force pixels on the screen
    for i in range(len(words_to_show)):
        oled.text(words_to_show[i], 64 - (len(words_to_show[i]) * 4), (i * 9) + 1, 1)
        oled.show()
        sleep(0.3)
        
    # draw the bounding box for the progress bar
    oled.line(10,  55, 117, 55, 1)
    oled.line(10,  60, 117, 60, 1)
    oled.line(10,  55, 10,  60, 1)
    oled.line(117, 55, 117, 60, 1)
    oled.show()
    
    # fill the progress bar, just for fun and visual flare
    for i in range(12, 116):
        oled.fill_rect(i, 57, 1, 2, 1)
        oled.show()
        
    # flash the whole screen white, also for fun 
    oled.fill(1)
    oled.show()
    sleep(0.2)
    oled.fill(0)
    oled.show()

# call and execute absolutely (not) nessesary loading screen
# if you want to disable "loading screen" just comment this line out
loading_screen(oled, rgb, led_user_1, led_user_2, buzzer)

# second core code
# this code is also not nessesary per se, but is responsible for muting behaviour and reset button behaviour
# there is already a resent button the the RP2040-Zero itself no actual need for the second one, you can repurpose it, as well as mute button
# another reason to ditch this second core and use it for something else is that each iteration it mutes buzzer it no button is pressed
# that makes it impossible to play sounds on a different core
# but if you delete this code then buttons on the main menu stop working
def second_core(up, right, left, down, action_a, action_b, mute, main_menu, buzzer):
    
    # define global variable that will be used by the main menu
    # globals are bad in programming generally speaking
    # especially in a multithreaded systems such as this one because of race conditions
    global is_up
    global is_down
    global is_left
    global is_right
    global is_a
    global is_b
    global is_mute
    global is_menu
    global buzzer_is_on
    
    # this variable is needed to detect the rising edge of the button press, to trigger once and not all the time
    previous_mute_state = 0
    
    while(True):
        
        # dumbass part of code that just invers the the state of the button variable and stores in a different variable
        # again, if removed breakes main menu behaviour and mute behaviour and custom reset button
        # inversion could have been done in the hardware, pulling down input pins and wiring buttons to the 3v3 volts
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
            
        # mute button t-trigger behaviour for the rising edge of the button press
        if (previous_mute_state != is_mute):
            if (is_mute == True):
                if (led_mute.value() == 0):
                    led_mute.value(1)
                    buzzer_is_on = False
                else:
                    led_mute.value(0)
                    buzzer_is_on = True
        previous_mute_state = is_mute

        # this code is resposible for button making sounds
        # it also mutes all sounds  when no buttons are pressed
        # making it impossible to play sounds on other cores when this code is active
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
        
        # this code reboots the MCU when "main menu" is pressed
        # since there are no parallel capacitors to the buttons sometimes it softlocks the game because of countact bouce
        # as previously mentioned this button better be repurposed to some other function
        # arternatively a software timer could be implemented to reset tetris after a long press
        if (is_menu):
            machine.reset()

# start "second_core" code on second core
# second core can't run two threads at once, but by this time "loading_screen_tune" has already finished
# do be careful when changing timings of the loading screen sequence, because it might produce a softlock
_thread.start_new_thread(second_core, (up, right, left, down, action_a, action_b, mute, main_menu, buzzer))

# reads the voltage of the battery once when the game is booted and store in a variable
read_voltage = batt_voltage.read_u16()

# variables needed to trigger on the rising edge of button press in the main menu
previous_up_state = 0
previous_right_state = 0
previous_left_state = 0
previous_down_state = 0
previous_a_state = 0
previous_b_state = 0

# start the main menu with the first item highlighed
list_hightlight = 1

while (True):
    
    # draw the "main menu" and battery level at the top and at the bottom of the screen
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
    
    # handle the botton presses to move the highlight up and down with direction buttons
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
    
    # run the game function after action button click depending on what item was highlighted
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
    
    # draw the white rectangle in a position corresponding to the highlighted game 
    oled.fill_rect(0, list_hightlight * 11 - 1, 127, 10, 1)
    
    # draw the names of the hame in white except for the highlighted game
    # still not sure how it works but it works
    oled.text(game_01.get_game_name(), 0, 11, list_hightlight - 1)
    oled.text(game_02.get_game_name(), 0, 22, list_hightlight - 2)
    oled.text(game_03.get_game_name(), 0, 33, list_hightlight - 3)
    oled.text(game_04.get_game_name(), 0, 44, list_hightlight - 4)
    