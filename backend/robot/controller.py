from sensors.motor import Motor
from sensors.rgb_leds import RGBLEDs
from robot.config import *
import sys
import tty
import termios

def get_key_press():
    """Attend et retourne une touche pressée (sans valider Entrée)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

rgb_leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
# Instance globale du moteur
motor = Motor()


def set_motor_speed(speed):
    motor.set_speed(speed)
    return f"Speed set to {speed}"

def stop_motor():
    motor.stop()
    return "Motor stopped"

def start_colors():
    print("Appuie sur r/g/b/u/v/n pour allumer une LED, q pour quitter.")
    while True:
        key = get_key_press()
        if key == 'q':
            print("Arrêt du contrôle des LEDs.")
            break
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
            print(f"LED {led} allumée à {value}")
        else:
            print("Touche non reconnue")

    
