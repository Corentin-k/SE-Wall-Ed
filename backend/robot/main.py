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
    # Couleurs à détecter
    COLOR_RANGES = {
        'Rouge': ([0, 150, 120], [5, 255, 255], (0, 0, 255)),
        'Vert': ([35, 80, 60], [90, 255, 255], (0, 255, 0)),
        'Bleu': ([105, 120, 50], [130, 255, 255], (255, 0, 0)),
        'Jaune': ([18, 100, 100], [35, 255, 255], (0, 255, 255)),
    }
    
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
        
        # Activation de la détection de couleur
        self.color_detection_enabled = True
        self.detected_colors = []

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
        if self.color_detection_enabled:
            return self.get_camera_frame_with_colors()
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
        self.motor.smooth_speed(0)
        self.motor_servomotor.set_angle(90)
        time.sleep(0.5)

    def set_emergency_mode(self, active: bool):
            if active:
                self.shutdown_robot()
            else:
                self.__init__()

    def shutdown_robot(self):
        try:
            self.stop_robot()
            self.shutdown_head()

            if self.controller:
                try:
                    self.set_controller(None)
                except Exception as e:
                    print(f"Erreur arrêt contrôleur : {e}")
                self.controller = None

            for sensor in [self.camera, self.ultra, self.line_tracker, self.buzzer,self.ws2812,self.pan_servo, self.tilt_servo, self.motor_servomotor, self.leds]:
                if sensor:
                    try:
                        sensor.shutdown()
                    except Exception as e:
                        print(f"Erreur lors de l'arrêt du capteur {sensor.__class__.__name__} : {e}")

            print("✔️ Shutdown complet")
        except Exception as e:
            print(f"Erreur inattendue pendant le shutdown: {e}")

    def detect_and_draw_colors(self, frame):
        """
        Détecte et dessine les couleurs sur l'image
        :param frame: Image OpenCV (format BGR)
        :return: Liste des couleurs détectées
        """
        if not self.color_detection_enabled:
            return []
            
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        detected_colors = []

        for name, (lower, upper, bgr_color) in self.COLOR_RANGES.items():
            lower_np = np.array(lower)
            upper_np = np.array(upper)
            mask = cv2.inRange(hsv, lower_np, upper_np)
            
            # Filtrage morphologique pour réduire le bruit
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Trouver les contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                if cv2.contourArea(cnt) > 500:  # Seuil de taille minimum
                    x, y, w, h = cv2.boundingRect(cnt)
                    # Dessiner le rectangle
                    cv2.rectangle(frame, (x, y), (x + w, y + h), bgr_color, 2)
                    # Ajouter le texte
                    cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, bgr_color, 2)
                    detected_colors.append({
                        'name': name,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2
                    })
                    break  # Une seule détection par couleur

        self.detected_colors = detected_colors
        return detected_colors

    def get_camera_frame_with_colors(self):
        """
        Récupère une frame de la caméra avec détection de couleur
        :return: Frame JPEG encodée avec annotations de couleur
        """
        try:
            # Récupérer la frame JPEG de la caméra
            frame_bytes = self.camera.get_frame()
            if frame_bytes is None:
                return None

            # Décoder l'image JPEG en format OpenCV
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                return frame_bytes  # Retourner la frame originale si décodage échoue

            # Optionnel : retourner l'image horizontalement
            frame = cv2.flip(frame, 1)

            # Appliquer la détection de couleur
            detected = self.detect_and_draw_colors(frame)
            
            # Log des couleurs détectées (optionnel)
            if detected:
                color_names = [color['name'] for color in detected]
                logger.debug(f"Couleurs détectées: {color_names}")

            # Ré-encoder l'image en JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()

        except Exception as e:
            logger.error(f"Erreur lors de la détection de couleur: {e}")
            # En cas d'erreur, retourner la frame originale
            return self.camera.get_frame()

    def enable_color_detection(self, enabled=True):
        """
        Active ou désactive la détection de couleur
        :param enabled: True pour activer, False pour désactiver
        """
        self.color_detection_enabled = enabled
        logger.info(f"Détection de couleur {'activée' if enabled else 'désactivée'}")

    def get_detected_colors(self):
        """
        Retourne la liste des couleurs actuellement détectées
        :return: Liste des couleurs avec leurs positions
        """
        return self.detected_colors.copy()

    def set_color_detection_threshold(self, threshold):
        """
        Modifie le seuil de détection (taille minimum des objets)
        :param threshold: Nouveau seuil en pixels
        """
        # Cette méthode pourrait être étendue pour modifier dynamiquement le seuil
        logger.info(f"Seuil de détection mis à jour: {threshold}")

def tests(robot):
    print("Doing some tests...")
    result = radar_scan(robot)
    min_angle, max_angle = result.get_nearest_obstacle_limits()
    print("nearest obstacle : ", min_angle, max_angle)
    robot.pan_servo.set_angle((min_angle + max_angle) / 2)

