# robot/main.py
import logging
import sys
import os
import busio

<<<<<<< HEAD
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import threading
import time
=======
import busio

from adafruit_pca9685 import PCA9685
from board import SCL, SDA


>>>>>>> 87e4cc9 (things are changing)
from sensors import *

from robot.config import *


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

class Robot:
    def __init__(self):
        self.motor = Motor()
        self.camera = Camera()
        self.leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
        self.leds.setup()

        self.init_servo_head()

        self._head_thread = None
        self._head_running = False
        self._head_lock = threading.Lock()

        logger.info("Robot initialized")

    def init_servo_head(self):
        i2c = busio.I2C(SCL, SDA)
        pca = PCA9685(i2c, address=0x5f) 
        pca.frequency = 50 

        PAN_CHANNEL = 1  
        TILT_CHANNEL = 2 
        
        self.pan_servo = ServoMotors(pca, channel=PAN_CHANNEL, initial_angle=90, step_size=2)
        self.tilt_servo = ServoMotors(pca, channel=TILT_CHANNEL, initial_angle=90, step_size=2)
    
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

    def get_camera_frame(self):
        return self.camera.get_frame()
        
    def movehead(self, pan, tilt):
        """
        Déplace la tête du robot en ajustant les servos de panoramique et d'inclinaison.
        :param pan: 1 pour tourner à droite, -1 pour tourner à gauche
        :param tilt: 1 pour monter, -1 pour descendre
        """
        if pan != 0:
            self.pan_servo.move_increment(pan)
        if tilt != 0:
            self.tilt_servo.move_increment(tilt)
            
    def _head_loop(self, pan: int, tilt: int, interval: float = 0.05):
        while True:
            with self._head_lock:
                if not self._head_running:
                    break
            self.movehead(pan, tilt)
            time.sleep(interval)
        # remise à 0/0 en sortie
        self.movehead(0, 0)

    def start_head(self, pan: int, tilt: int):
        with self._head_lock:
            # si déjà en cours, on coupe l’ancienne boucle
            if self._head_running:
                self._head_running = False
                if self._head_thread:
                    self._head_thread.join()
            # on lance la nouvelle
            self._head_running = True
            self._head_thread = threading.Thread(
                target=self._head_loop, args=(pan, tilt), daemon=True
            )
            self._head_thread.start()

    def stop_head(self):
        with self._head_lock:
            self._head_running = False
        if self._head_thread:
            self._head_thread.join()

# main
