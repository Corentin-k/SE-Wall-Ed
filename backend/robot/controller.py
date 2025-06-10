from sensors.motor import Motor
from sensors.rgb_leds import RGBLEDs
from robot.config import *

rgb_leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
# Instance globale du moteur
motor = Motor()
rgb_leds = RGBLEDs(13, 19, 0, 1, 5, 6)

def set_motor_speed(speed):
    motor.set_speed(speed)
    return f"Speed set to {speed}"

def stop_motor():
    motor.stop()
    return "Motor stopped"

def set_led_by_key(key):
    mapping = {
        'r': ('L_R', 255),  
        'g': ('L_G', 255),  
        'b': ('L_B', 255),  
        'u': ('R_R', 255), 
        'v': ('R_G', 255),  
        'n': ('R_B', 255),  
    }
    if key in mapping:
        led, value = mapping[key]
        rgb_leds.highled(led, value)
        return f"LED {led} allumée à {value}"
    else:
        return "Touche non reconnue"

    
