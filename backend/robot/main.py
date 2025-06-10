# robot/main.py
import logging
from sensors.motor import Motor

logger = logging.getLogger(__name__)

class Robot:
    def __init__(self):
        self.motor = Motor()
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

    
# main
if __name__ == "__main__":
    robot = Robot()
    robot.move_forward(5)
    robot.stop()
    print("Robot operations completed.")