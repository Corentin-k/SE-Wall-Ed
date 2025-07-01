import threading
import time
import logging
from sensors import *
from robot.config import *
import asyncio
import cv2
import numpy as np

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
        
        # Contrôleur de détection de couleur
        self.color_controller = None
        # Activer la détection de couleur par défaut
        self.enable_color_detection(True)

        # self.init_controller_thread()
        logger.info("Robot initialized")
        # tests(self)

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
        """
        Récupère une frame de la caméra avec ou sans détection de couleur
        """
        if self.color_controller and self.color_controller.enabled:
            return self.color_controller.get_camera_frame_with_colors()
        else:
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
                self.motor_servomotor.set_angle(0)
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
        self.motor.smooth_speed(0)
        self.motor_servomotor.set_angle(0)
        time.sleep(0.5)

    def set_emergency_mode(self, active: bool):
        if active:
            self.shutdown_robot()
        else:
            try:
                self.__init__()
            except Exception as e:
                print(f"Erreur lors de la réinitialisation du robot : {e}")

    def shutdown_robot(self):
        """Arrêt propre et sécurisé du robot"""
        print("Début de l'arrêt du robot")
        try:
            # Arrêt des mouvements
            self.stop_robot()
            
            # Arrêt de la tête
            if hasattr(self, '_head_thread') and self._head_thread.is_alive():
                self.shutdown_head()

            # Arrêt du contrôleur
            if self.controller:
                try:
                    self.set_controller(None)
                except Exception as e:
                    print(f"Erreur arrêt contrôleur : {e}")
                self.controller = None

            # Arrêt des capteurs et actuateurs
            components = [
                ('camera', self.camera),
                ('ultrasonic', self.ultra),
                ('line_tracker', self.line_tracker),
                ('buzzer', self.buzzer),
                ('ws2812', self.ws2812),
                ('pan_servo', self.pan_servo),
                ('tilt_servo', self.tilt_servo),
                ('motor_servo', self.motor_servomotor),
                ('leds', self.leds)
            ]
            
            for name, component in components:
                if component:
                    try:
                        if hasattr(component, 'shutdown'):
                            component.shutdown()
                    except Exception as e:
                        print(f"Erreur lors de l'arrêt de {name}: {e}")

        except Exception as e:
            print(f"Erreur inattendue pendant le shutdown: {e}")

    def update_speed(self, speed: int):
        """Met à jour la vitesse du robot"""
        if 0 <= speed <= 100:
            self.speed = speed
        else:
            raise ValueError("Speed must be between 0 and 100")

    # -------------------- Méthodes de détection de couleur -------------------
    def enable_color_detection(self, enabled: bool = True):
        """Active ou désactive la détection de couleur"""
        if enabled and self.color_controller is None:
            from robot.color_detection import ColorDetectionController
            self.color_controller = ColorDetectionController(self)
        
        if self.color_controller:
            self.color_controller.enable_detection(enabled)
    
    @property
    def color_detection_enabled(self) -> bool:
        """Retourne l'état de la détection de couleur"""
        return self.color_controller is not None and self.color_controller.enabled
    
    def get_detected_colors(self) -> list:
        """Retourne les couleurs actuellement détectées"""
        if self.color_controller:
            return self.color_controller.get_detected_colors()
        return []

def tests(robot):
    print("Doing some tests...")
    result = radar_scan(robot)
    min_angle, max_angle = result.get_nearest_obstacle_limits()
    print("nearest obstacle : ", min_angle, max_angle)
    robot.pan_servo.set_angle((min_angle + max_angle) / 2)
