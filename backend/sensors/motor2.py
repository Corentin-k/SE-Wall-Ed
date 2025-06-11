import logging

logger = logging.getLogger(__name__)

class Motor:
    def __init__(self):
        self.speed = 0
        logger.info("Motor initialized with speed: %d", self.speed)

    def set_speed(self, speed: int):
        self.speed = speed
        logger.info("Motor speed set to: %d", self.speed)

    def stop(self):
        self.speed = 0
        logger.info("Motor stopped")

    def move(self, direction: str):
        if direction == 'forward':
            self.set_speed(self.speed)
        elif direction == 'backward':
            self.set_speed(-self.speed)
        elif direction == 'left':
            logger.info("Motor turning left at speed: %d", self.speed)
        elif direction == 'right':
            logger.info("Motor turning right at speed: %d", self.speed)
        else:
            self.stop()
        logger.info("Motor moving %s at speed: %d", direction, self.speed)
