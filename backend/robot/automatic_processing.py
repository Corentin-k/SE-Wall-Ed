import time
import threading
import cv2
import numpy as np
from robot.controller import Controller
from robot.camera_processing import Arrow, persistent_arrow_detector, get_arrow_direction

class LabyrinthNavigationController(Controller):
    """
    Contrôleur pour la navigation automatique dans un labyrinthe.
    Utilise la détection de flèches pour déterminer la direction et évite les obstacles.
    """
    
    # def __init__(self, robot):
    #     super().__init__(robot)
    #     self.robot = robot
    #     self.enabled = False
    #     self.stop_navigation = False
    #     self.time_turn= 0
    #     self.turning = False
    #     # Paramètres de navigation
    #     self.forward_speed = 20  # Vitesse d'avancement
    #     self.turn_duration = 1.0  # Durée des virages en secondes
    #     self.obstacle_distance_threshold = 30  # Distance d'arrêt en cm
    #     self.arrow_check_interval = 0.5  # Intervalle de vérification des flèches
    #     self.movement_step_duration = 0.5  # Durée d'un pas d'avancement
    
    #     self.last_arrow_direction = None
        
    #     # Détection de flèches
    #     self.arrow_detection_enabled = True
    #     self.detected_arrow = None
        
    #     # États de navigation (initialisés dans start())
    #     self.navigation_state = "FORWARD"
    #     self.turn_start_time = 0
    #     self.arrow_check_start_time = 0
    #     self.backup_start_time = 0
        
    
    # def start(self):
    #     """Démarre la navigation automatique"""
    #     if not self.enabled:
    #         self.enabled = True
    #         self.stop_navigation = False

    #         try:
    #             self.robot.move_robot(0)
    #             self.robot.pan_servo.set_angle(90)            
    #             # Activer les détections nécessaires
    #             if hasattr(self.robot, 'enable_arrow_detection'):
    #                 self.robot.enable_arrow_detection(True)
                
    #             # Initialiser l'état de navigation
    #             self.navigation_state = "FORWARD"
    #             self.turn_start_time = 0
    #             self.arrow_check_start_time = 0
                
    #         except Exception as e:
    #             print(f"Erreur lors du démarrage de la navigation: {e}")
    #             self.enabled = False
    
    # def update(self):
    #     """Méthode appelée par la boucle du contrôleur de base"""
    #     if not self.enabled or self.stop_navigation:
    #         return
            
    #     try:
    #         self._navigation_step()
    #     except Exception as e:
    #         print(f"Erreur dans la navigation: {e}")
    #         self.enabled = False
    
    # def on_stop(self):
    #     """Arrête la navigation automatique"""
    #     self.enabled = False
    #     self.stop_navigation = True
    #     self.current_state = "STOPPED"
        
    #     # Arrêter le robot
    #     self.robot.move_robot(0)
    #     self.robot.change_direction(0)
        
    #     print("Stop maze")
    
    # def enable_arrow_detection(self, enabled=True):
    #     """
    #     Active ou désactive la détection de flèches
    #     :param enabled: True pour activer, False pour désactiver
    #     """
    #     self.arrow_detection_enabled = enabled
    
    # def get_detected_arrow(self):
    #     """
    #     Retourne la dernière direction de flèche détectée
    #     :return: Direction ("left", "right", "up", "down") ou None
    #     """
    #     return self.detected_arrow
    
    # def get_camera_frame_with_arrows(self):
    #     """
    #     Récupère une frame de la caméra, détecte les flèches via Arrow/PersistentArrowDetector
    #     et les dessine sans modifier la classe Arrow.
    #     """
    #     try:
    #         frame_bytes = self.robot.camera.get_frame()
    #         if frame_bytes is None:
    #             return None

    #         # 1) Décodage du JPEG
    #         np_arr = np.frombuffer(frame_bytes, np.uint8)
    #         frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    #         if frame is None:
    #             return frame_bytes

    #         # 2) Détection : on utilise find_arrows qui construit et push des Arrow
    #         find_arrows(frame)

    #         # 3) Récupère la détection la plus fiable
    #         detection = persistent_arrow_detector.get_max_hit_arrow()
    #         if detection:
    #             # Afficher simplement la flèche détectée sur la frame
    #             detection.arrow.draw(frame)
    #             self.detected_arrow = get_arrow_direction()
    #         else:
    #             self.detected_arrow = None

    #         # 6) Ré-encodage et retour
    #         _, buffer = cv2.imencode('.jpg', frame)
    #         return buffer.tobytes()

    #     except Exception as e:
    #         print(f"Erreur détection flèches via Arrow : {e}")
    #         return self.robot.camera.get_frame()
    
    # def _navigation_step(self):
    #     """Une étape de navigation appelée par le contrôleur de base"""
    #     if not hasattr(self, 'navigation_state'):
    #         self.navigation_state = "FORWARD"
    #         self.turn_start_time = 0
    #         self.arrow_check_start_time = 0
    #         self.backup_start_time = 0
        
    #     current_distance = self.robot.ultra.get_distance_cm()
    #     if self.navigation_state == "FORWARD":
    #         # Avancer tant qu'il n'y a pas d'obstacle
    #         if current_distance > self.obstacle_distance_threshold:
    #             if self.turning and (time.time() - self.time_turn > 2.5):
    #                 # Si on est en train de tourner, on s'arrete de tourner
    #                 self.robot.change_direction(0)
    #                 time.sleep(0.2)
    #                 self.turning = False
    #                 self.time_turn = 0
    #             # si les roue sont en train de tourner, on lance
    #             self.robot.move_robot(self.forward_speed)
    #         else:
    #             # Obstacle détecté, arrêter et passer à la lecture de flèche
    #             self.robot.move_robot(0)
    #             self.navigation_state = "READING_ARROW"
    #             self.arrow_check_start_time = time.time()
    #             self.detected_arrow = None  # Reset de la détection
        
    #     elif self.navigation_state == "READING_ARROW":
    #         # Lire les flèches pendant un certain temps
    #         self._check_and_process_arrow()
    #         tab_arrows=[]
    #         for _ in range(5):
    #             # Essayer de lire la flèche plusieurs fois pour plus de fiabilité
    #             # lire 5 fois la valeur espacer de 0.5 secondes et prendre la valeur la plus fréquente
    #             time.sleep(0.5)
    #             tab_arrows.append(self.get_detected_arrow())
    #             print(f"Direction de flèche lue: {tab_arrows[-1]}")
    #         arrow_direction = max(set(tab_arrows), key=tab_arrows.count) if tab_arrows else None
    #         # Passer au recul, peu importe si une flèche est détectée ou non
    #         self.navigation_state = "BACKING_UP"
    #         self.backup_start_time = time.time()
    #         self.robot.move_robot(-self.forward_speed)  # Reculer
    #     elif self.navigation_state == "BACKING_UP":
    #         # Reculer pendant 1.7 secondes
    #         if time.time() - self.backup_start_time < 1.7:
    #             # Continuer à reculer
    #             self.robot.change_direction(0)  
    #             self.robot.move_robot(-self.forward_speed)
    #         else:
    #             # Fin du recul, arrêter et passer au virage
    #             self.robot.move_robot(0)
                
    #             arrow_direction = self.get_detected_arrow()
    #             if arrow_direction in ["left", "right"]:
    #                 self.time_turn = time.time()
    #                 self.turning = True
    #                 if arrow_direction == "left":
    #                     self.robot.change_direction(30)  # Tourner à gauche
    #                     try:
    #                         self.robot.ws2812.set_all_led_color(0, 255, 0)  # Vert pour gauche
    #                     except:
    #                         pass
    #                 elif arrow_direction == "right":
    #                     self.robot.change_direction(-30)  # Tourner à droite
    #                     try:
    #                         self.robot.ws2812.set_all_led_color(0, 0, 255)  # Bleu pour droite
    #                     except:
    #                         pass
    #             else:
    #                 print("Aucune flèche détectée")
    #                 self.robot.change_direction(30)  # Virage par défaut à droite
    #                 self.robot.ws2812.set_all_led_color(255, 255, 0)  # Jaune pour défaut
    #                 pass
    #             self.robot.move_robot(20)
    #             time.sleep(1)
    #             self.navigation_state = "FORWARD"
    #             self.turn_start_time = time.time()
        
       
       
        
    #     else:
    #         # État inconnu, retour à l'avancement
    #         self.navigation_state = "FORWARD"
    
    # def _check_and_process_arrow(self):
    #     """Vérifie et traite la détection de flèches en temps réel"""
    #     try:
    #         # Récupérer la frame avec détection de flèches
    #         frame_with_arrows = self.get_camera_frame_with_arrows()
    #         # La détection se fait automatiquement dans get_camera_frame_with_arrows
    #         # qui met à jour self.detected_arrow
    #     except Exception as e:
    #         print(f"Erreur lors de la vérification des flèches: {e}")

    def __init__(self,robot):
        super().__init__(robot)
        self.last_arrow_direction = None
        pass
    
    def start(self):
        pass
    
    def update(self):
        camera_size = (640, 480)

        turn_angle = 30
        robot_speed = 18
        acceleration_rate = 100

        if self.robot.ultra.get_distance_cm() < 15:
            self.robot.motor.smooth_speed_and_wait(0, acceleration=acceleration_rate)
            print("wall")
            self.turn(self.last_arrow_direction)
        
        self.robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)

        detection = persistent_arrow_detector.get_max_hit_arrow()
        if detection == None:
            return
        
        detected_arrow = detection.arrow
        direction = "right" if detected_arrow.get_direction()[0] > 0 else "left"
        self.last_arrow_direction = direction
        arrow_center_offset = (detected_arrow.start[0] / camera_size[0]) * 2 - 1

        self.robot.change_direction(max(-turn_angle, min(turn_angle, turn_angle * -arrow_center_offset * 4)))

    def turn(self, direction):
        turn_angle = 30
        robot_speed = 30
        acceleration_rate = 100

        angle = -turn_angle if direction == "right" else turn_angle
        self.robot.change_direction(-angle)
        time.sleep(0.1)
        self.robot.motor.smooth_speed_and_wait(-robot_speed, acceleration=acceleration_rate)
        time.sleep(1.5)
        self.robot.motor.smooth_speed_and_wait(0, acceleration=acceleration_rate)
        time.sleep(0.5)
        self.robot.change_direction(angle)
        time.sleep(0.1)
        self.robot.motor.smooth_speed_and_wait(robot_speed, acceleration=acceleration_rate)
        time.sleep(2)
        self.robot.motor.smooth_speed_and_wait(0, acceleration=acceleration_rate)
        self.robot.change_direction(0)
        time.sleep(0.5)

        pass

    def stop(self):
        self.robot.motor.smooth_speed_and_wait(0)
        self.robot.change_direction(0)
        pass
