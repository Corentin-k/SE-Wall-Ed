# robot/main.py
import logging
import sys
import os

from sensors import *
from controller import start_colors
from robot.config import *


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class Robot:
    def __init__(self):
        self.motor = Motor()
        self.leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
        logger.info("Robot initialized")

    def move_forward(self, speed):
        logger.info("Robot moving forward at speed %d", speed)
        self.motor.set_speed(speed)

    def move_backward(self, speed):
        logger.info("Robot moving backward at speed %d", speed)
        self.motor.set_speed(-speed)

    def turn_left(self, speed):
        logger.info("Robot turning left")
        # Implémentation réelle dépend du matériel
        self.motor.move("left")

    def turn_right(self, speed):
        logger.info("Robot turning right")
        # Implémentation réelle dépend du matériel
        self.motor.move("right")

    def stop(self):
        logger.info("Robot stopping")
        self.motor.stop()
    def led(self,hex):
         self.leds.set_color_hex(hex)

# main
if __name__ == "__main__":
    robot = Robot()
    robot.led("#FF8800")
    print("Robot operations completed.")