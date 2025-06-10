from sensors.motor2 import Motor
from sensors.rgb_leds import RGBLEDs
from robot.config import *

rgb_leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
# Instance globale du moteur
motor = Motor()


def set_motor_speed(speed):
    motor.set_speed(speed)
    return f"Speed set to {speed}"

def stop_motor():
    motor.stop()
    return "Motor stopped"



    
