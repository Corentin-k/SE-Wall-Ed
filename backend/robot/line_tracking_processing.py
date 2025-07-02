import threading
import time
from robot.controller import Controller
from robot.radar_scan_utils import *

class LineTrackingController(Controller):
    """
    Contrôleur pour le suivi de ligne du robot.
    Il gère l'activation et la désactivation du suivi de ligne.
    """

    def __init__(self, robot):
        super().__init__(robot)
        self._previous_middle = 0
        self._white_detected_time = None
        self._pointille_delay = 0.8
        self._last_line_time = time.time()  # Dernière fois qu'on a vu la ligne
        self._right_angle_timeout = 3.0  # Timeout pour détecter un angle droit
        self._search_timeout = 5.0       # Timeout pour la recherche de ligne
        self._performing_right_angle = False  # Flag pour indiquer qu'on effectue un angle droit
        self._search_start_time = None   # Temps de début de la recherche de ligne

        self.last_line_detected = None  # right or left

        self._lost_counter = 0
        self._lost_threshold = 3
        self._reverse_duration = 1.2  # Durée en secondes pour reculer fort

    def start(self):
         """
         Active le mode de suivi de ligne du robot.
         Ceci démarrera la boucle de traitement de ligne du LineTracker
         """
         self.robot.move_robot(0)
         self.robot.change_direction(0)
         self.robot.pan_servo.set_angle(90)
         time.sleep(0.1)

    def update(self):
        print("[Suivi ligne] Mise à jour du suivi de ligne...")
        status = self.robot.line_tracker.read_sensors()
        left = status['left']
        middle = status['middle']
        right = status['right']
        robot_speed = 40
        acceleration_rate = 350
        turn_angle_left = 30
        turn_angle_right = -30

        # if self.robot.ultra.get_distance_cm() < 40:
        #     pass
        #     #print("[Obstacle] Obstacle détecté, changement de mode...")
        #     self.robot.motor.smooth_speed_and_wait(0)
        #     self.avoid_obstacle(-1)
        #     return

        if self._performing_right_angle:
            # Si on est déjà en train de chercher la ligne, ne pas interférer
            return

        if left == 0 and middle == 0 and right == 0:
            # Pas de ligne détectée
            self._lost_counter += 1
            #print(f"[Suivi ligne] Ligne perdue ({self._lost_counter}/{self._lost_threshold})")

            if self._lost_counter >= self._lost_threshold:
                #print("[Suivi ligne] Seuil de perte atteint, déclenchement de la recherche")
                self._performing_right_angle = True
                self._lost_counter = 0
                self.perform_right_angle()
                return
        else:
            # Ligne détectée => reset du compteur
            if self._lost_counter > 0:
                #print(f"[Suivi ligne] Ligne retrouvée! Reset du compteur de perte")
                self._lost_counter = 0

            # Mémoriser la dernière direction où on a vu la ligne
            if left == 1:
                self.last_line_detected = 'left'
            elif right == 1:
                self.last_line_detected = 'right'


        print("left: {left}   middle: {middle}   right: {right}".format(**status))
        status = self.robot.line_tracker.read_sensors()
        left = status['left']
        middle = status['middle']
        right = status['right']
        print("left: {left}   middle: {middle}   right: {right}".format(**status))
        if middle == 1:
            if self._previous_middle == 0:
                self.robot.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward
            if left == 0 and right == 1:
                print("Adjusting right (line slightly left)")
                self.robot.change_direction(turn_angle_right-10)
                self.robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)
            elif left == 1 and right == 0:
                print("Adjusting left (line slightly right)")
                self.robot.change_direction(turn_angle_left-10)
                self.robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)
            else:
                self.robot.change_direction(0)
                print("Going straight (middle detected)")
                self.robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)
        else:
            if self._previous_middle == 1:
                self.robot.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward
            if left == 1:
                print("Turning left to find line")
                self.robot.change_direction(turn_angle_right)
                self.robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate)
            elif right == 1:
                print("Turning right to find line")
                self.robot.change_direction(turn_angle_left)
                self.robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate)
            else:
                print("NOOOO we lost the line :(")
                self.robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate)
        self._previous_middle = middle


    def perform_right_angle(self):
        """
        Stratégie de recherche de ligne quand elle est perdue :
        1. Reculer légèrement pour éviter les obstacles
        2. Avancer vers la gauche et attendre la détection de ligne
        3. Si détection de ligne : retourner au suivi de ligne normal
        4. Sinon reculer dans la même direction et tourner vers la droite
        5. Si ligne détectée à droite : réactiver le suivi de ligne
        """
        #print("[Recherche ligne] Perte de ligne détectée, début de la procédure de recherche...")

        # Étape 1: Reculer légèrement pour éviter les obstacles
        #print("[Recherche ligne] Étape 1: Recul de sécurité...")
        self.robot.motor.smooth_speed_and_wait(-30, acceleration=300)
        time.sleep(0.5)  # Recul court
        self.robot.motor.smooth_speed_and_wait(0)

        # Étape 2: Avancer vers la gauche et chercher la ligne
        #print("[Recherche ligne] Étape 2: Recherche vers la gauche...")
        self.robot.change_direction(-30)  # Tourner à gauche
        time.sleep(0.2)  # Laisser le temps de positionner les roues

        # Avancer en cherchant la ligne
        self.robot.motor.smooth_speed(35)  # Vitesse réduite pour la recherche
        search_start = time.time()
        line_found = False

        while time.time() - search_start < 3.5:  # Timeout de 2.5 secondes
            sensors = self.robot.line_tracker.read_sensors()
            if (sensors['middle'] == 1 or sensors['left'] == 1 or sensors['right'] == 1) and time.time() - self._last_line_detected >1 :
                #print("[Recherche ligne] ✓ Ligne retrouvée vers la gauche!")
                self.robot.motor.smooth_speed_and_wait(0)
                self.robot.change_direction(0)  # Remettre direction droite
                time.sleep(0.3)
                self._performing_right_angle = False
                line_found = True
                return
            time.sleep(0.05)  # Vérification fréquente

        # Étape 3: Si pas trouvé à gauche, arrêter et reculer
        if not line_found:
            #print("[Recherche ligne] Ligne non trouvée à gauche, recul...")
            self.robot.motor.smooth_speed_and_wait(0)

            # Reculer dans la même direction (toujours tourné à gauche)
            self.robot.motor.smooth_speed(-25)
            time.sleep(1.0)  # Reculer suffisamment
            self.robot.motor.smooth_speed_and_wait(0)

            # Étape 4: Tourner vers la droite et chercher
            #print("[Recherche ligne] Étape 4: Recherche vers la droite...")
            self.robot.change_direction(30)  # Tourner à droite
            time.sleep(0.2)

            # Avancer vers la droite en cherchant
            self.robot.motor.smooth_speed(25)
            search_start = time.time()

            while time.time() - search_start < 3.5:  # Timeout de 3.5 secondes
                sensors = self.robot.line_tracker.read_sensors()
                if sensors['middle'] == 1 or sensors['left'] == 1 or sensors['right'] == 1:
                    #print("[Recherche ligne] ✓ Ligne retrouvée vers la droite!")
                    self.robot.motor.smooth_speed_and_wait(0)
                    self.robot.change_direction(0)  # Remettre direction droite
                    time.sleep(0.3)
                    self._performing_right_angle = False
                    line_found = True
                    return
                time.sleep(0.05)

        # Étape 5: Si toujours rien trouvé, arrêter et reprendre le mode normal
        if not line_found:
            #print("[Recherche ligne] ⚠ Ligne introuvable après recherche complète")
            self.robot.motor.smooth_speed_and_wait(0)
            self.robot.change_direction(0)  # Direction neutre
            self._performing_right_angle = False

            # Optionnel: faire une rotation sur place pour chercher dans toutes les directions
            #print("[Recherche ligne] Tentative de rotation sur place...")


    def on_stop(self):
        super().on_stop()
        self.robot.line_tracker.shutdown()

    def avoid_obstacle(self, direction):
        seuil_obstacle = 40
        trop_proche = 20
        vitesse = 40

        print("[Obstacle] Démarrage du contournement...")

        # Étape 1 : roue à gauche ou à droite
        if direction < 0:
            angle = -30
        else:
            angle = 30
        # angle = map_range(angle, -103, 77, 0, 180)
        self.robot.change_direction(angle)

        # Étape 2 : tant que l’obstacle est devant, avancer et vérifier la proximité
        dist = self.robot.ultra.get_distance_cm()
        previous_state = 0
        state = 0
        while dist < seuil_obstacle:
            if dist < trop_proche:
                state = 1
                if previous_state == 0:
                    self.robot.motor.smooth_speed_and_wait(0)
                    if direction <0:
                        angle = -30
                    else:
                        angle = 30
                    # angle = map_range(angle, -103, 77, 0, 180)
                    self.robot.change_direction(angle)
                self.robot.motor.smooth_speed(-vitesse)
            else:
                state = 0
                if previous_state == 1:
                    self.robot.motor.smooth_speed_and_wait(0)
                    if direction <0:
                        angle = -30
                    else:
                        angle = 30
                    # angle = map_range(angle, -103, 77, 0, 180)
                    self.robot.change_direction(angle)
                self.robot.motor.smooth_speed(vitesse)

            previous_state = state
            dist = self.robot.ultra.get_distance_cm()

        # Étape 3 : roue droite pour se réaligner
        self.robot.motor.smooth_speed_and_wait(0, acceleration=150)
        angle = 0
        # angle = map_range(angle, -103, 77, 0, 180)
        self.robot.change_direction(angle)

        # Étape 4 : scan pour détecter l’angle avec la plus grande distance
        result = radar_scan(self.robot)
        min_angle, max_angle = result.get_nearest_obstacle_limits()
        #angle = map_range(max_angle, -103, 77, 0, 180)
        if max_angle > 30:
            max_angle = 30
        else:
            max_angle = -30
        self.robot.change_direction(max_angle)

        # Étape 5 : avancer jusqu’à ce que l’obstacle ait disparu du champ de vision
        self.robot.motor.smooth_speed(vitesse, acceleration=150)  # Avancer à vitesse constante
        # time.sleep(1)

        # Étape 6 : tourner pour revenir vers l’axe de la ligne
        if direction <0:
            angle = 30
        else:
            angle = -30
        # angle = map_range(angle, -103, 77, 0, 180)
        self.robot.change_direction(angle)  # Tourne à droite
        time.sleep(0.1)
        self.robot.motor.smooth_speed(vitesse, acceleration=150)
        while self.robot.line_tracker.read_sensors()['middle'] == 0:
            pass

        self.robot.motor.smooth_speed_and_wait(0, acceleration=150)


        # Etape 7 : arrêter le robot / ToDo : relancer line tracking
        """self.robot.motor.smooth_speed(0)
        angle = 0
        # angle = map_range(angle, -103, 77, 0, 180)
        self.robot.change_direction(angle)  # Roue droite
        self.robot.pan_servo.set_angle(0)"""
        print("[Obstacle] Contournement terminé. Reprise du suivi de ligne.")
