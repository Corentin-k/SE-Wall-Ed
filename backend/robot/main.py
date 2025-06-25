import threading
import time
import logging
from sensors import *
from robot.config import *
import asyncio

from robot.radar_processing import *
from robot.line_tracking_processing import *

logger = logging.getLogger(__name__)

def map_range(x,in_min,in_max,out_min,out_max):
        return (x - in_min)/(in_max - in_min) *(out_max - out_min) +out_min

class Robot:
    def __init__(self):
        # Initialisation des composants
        self.camera = Camera()
        self.ultra = UltrasonicSensor()
        self.speed = 50
        self.init_servo_head()
        self.controller = None
        self.controller_lock = threading.Lock()

        self.init_movement()

        self.init_leds()

        self.buzzer = Buzzer()

        self.line_tracker = None

        self.init_controller_thread()
        logger.info("Robot initialized")
        tests(self)

    # -------------------- Initialisation des composants -------------------
    def init_controller_thread(self):
        """
        Initialise le thread pour le contrôleur du robot.
        """
        self.controller_thread = threading.Thread(target=self._controller_loop, daemon=True)
        self.controller_thread.start()

    def init_servo_head(self):
        """
        Initialise les deux servomoteurs de la tête
        """
        self.pan_servo = ServoMotors(channel=PAN_CHANNEL, initial_angle=90, step_size=2)
        self.tilt_servo = ServoMotors(channel=TILT_CHANNEL, initial_angle=90, step_size=2)

        # Variables pour le pilotage de la tête
        self._pan = 0
        self._tilt = 0
        self._head_running = True
        self._head_lock = threading.Lock()
        self.result = []

        # Centrage initial de la tête
        self.move_head(0, 0)

        # Lancement du thread de mouvement de la tête
        self._head_thread = threading.Thread(target=self._head_loop, daemon=True)
        self._head_thread.start()

    def init_movement(self):
        """
        Initialise les moteurs pour le mouvement du robot.
        """
        self.motor = Motors()
        self.motor_servomotor = ServoMotors(channel=MOTOR_CHANNEL, initial_angle=90, step_size=2)

    def init_leds(self):
        """
        Initialise les LEDs du robot.
        """
        self.leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
        self.leds.setup()
        self.ws2812 = WS2812LED(8, 255)
        self.ws2812.start()
    def _controller_loop(self):
        """
        Thread pour exécuter le contrôleur du robot.
        """
        while True:
            with self.controller_lock:
                if self.controller is not None:
                    self.controller.update()
            time.sleep(1/20)
    # -------------------- Méthodes de contrôle du robot -------------------

    def led(self, hex_color):
        self.leds.set_color_hex(hex_color)

    def get_camera_frame(self):
        return self.camera.get_frame()

    def move_head(self, pan, tilt):
        """
        Déplace la tête du robot en ajustant les servos de panoramique et d'inclinaison.
        :param pan: 1 pour tourner à droite, -1 pour tourner à gauche
        :param tilt: 1 pour monter, -1 pour descendre
        """
        if pan != 0:
            self.pan_servo.move_increment(pan)
        if tilt != 0:
            self.tilt_servo.move_increment(tilt)

    def _head_loop(self, interval: float = 0.05):
        while self._head_running:
            with self._head_lock:
                pan, tilt = self._pan, self._tilt
            self.move_head(pan, tilt)
            time.sleep(interval)
        self.move_head(0, 0)

    def start_head(self, pan: int, tilt: int):
        """
        Met à jour la consigne de pan et tilt (exécutée en continu par le thread).
        """
        with self._head_lock:
            self._pan = pan
            self._tilt = tilt

    def stop_head(self):
        """
        Arrête le mouvement de la tête (ramène pan/tilt à zéro) sans tuer le thread.
        """
        with self._head_lock:
            self._pan = 0
            self._tilt = 0

    def shutdown_head(self):
        """
        Termine proprement le thread de mouvement de la tête.
        """
        with self._head_lock:
            self._head_running = False
        self._head_thread.join()

    def move_robot(self, speed: int):
        self.motor.smooth_speed(speed)

    def change_direction(self, angle):
        self.motor_servomotor.set_angle(angle)

    def mode_police(self):
        """
        Met le robot en mode police.
        """
        if not self.leds:
            self.init_leds()
        if not self.ws2812:
            self.init_leds()
        if not self.buzzer:
            self.buzzer = Buzzer()
        self.leds.start_police(interval=0.3)
        self.ws2812.start_police(interval=0.05)
        threading.Thread(target=self.buzzer.play_tune, args=(None,"Police",), daemon=True).start()

    def stop_police(self):
        # Arrête le buzzer
        self.buzzer.stop()
        self.ws2812.stop_police()
        self.leds.stop_police()

    def set_controller(self, controller: Controller):
        with self.controller_lock:
            if self.controller:
                self.controller.stop()
                self.motor.smooth_speed(0)
                self.motor_servomotor.set_angle(90)
                self.stop_head()
            self.controller = controller
            if self.controller:
                if isinstance(self.controller, LineTrackingController):
                    self.line_tracker = LineTracker(
                        pin_left=line_pin_left,
                        pin_middle=line_pin_middle,
                        pin_right=line_pin_right
                    )
                self.controller.start_controller()


    def stop_robot(self):
        """
        Arrête les moteurs et réinitialise les servos à leur position centrale.
        """
        print("Stopping motors and resetting servos...")
        self.motor.smooth_speed(0)
        self.motor_servomotor.set_angle(90)
        time.sleep(0.5)


    def shutdown_robot(self):
        try:
            if self.controller:
                try:
                    self.set_controller(None)
                except Exception as e:
                    logger.warning(f"Erreur arrêt contrôleur : {e}")
                self.controller = None

            self.stop_robot()
            self.shutdown_head()

            if self.buzzer:
                try:
                    self.buzzer.shutdown()
                except Exception as e:
                    logger.warning(f"Erreur lors de l'arrêt du buzzer : {e}")

            for servo in [self.pan_servo, self.tilt_servo, self.motor_servomotor]:
                if servo:
                    try:
                        servo.stop()
                    except Exception as e:
                        logger.warning(f"Erreur arrêt servo : {e}")

            if self.ws2812:
                try:
                    self.ws2812.led_close()
                except Exception as e:
                    logger.warning(f"Erreur arrêt WS2812 : {e}")

            if self.leds:
                try:
                    self.leds.destroy()
                except Exception as e:
                    logger.warning(f"Erreur arrêt LEDs : {e}")

            if self.ultra:
                try:
                    self.ultra.shutdown()
                except Exception as e:
                    logger.warning(f"Erreur arrêt capteur ultra : {e}")

            if self.camera:
                try:
                    self.camera.shutdown()
                except Exception as e:
                    logger.warning(f"Erreur arrêt caméra : {e}")

            if self.line_tracker:
                try:
                    self.line_tracker.destroy()
                except Exception as e:
                    logger.warning(f"Erreur arrêt line tracker : {e}")

            logger.info("✔️ Shutdown complet")
        except Exception as e:
            logger.error(f"Erreur inattendue pendant le shutdown: {e}")

    def set_emergency_mode(self, active: bool):
        if active:
            self.shutdown_robot()

        else:
            self.__init__()


def tests(robot):
    print("Doing some tests...")
    result = radar_scan(robot)
    min_angle, max_angle = result.get_nearest_obstacle_limits()
    print("nearest obstacle : ", min_angle, max_angle)

