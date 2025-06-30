import time
import logging
from robot.controller import Controller
from robot.radar_scan_utils import *

logger = logging.getLogger(__name__)

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

class LineTrackingController(Controller):
    """
    Contrôleur pour le suivi de ligne du robot.
    Il gère l'activation et la désactivation du suivi de ligne.
    """

    def __init__(self, robot):
        super().__init__(robot)
        self._previous_middle = 0
        # Paramètres pour la détection des pointillés
        self._white_detected_time = None
        self._pointille_delay = 0.8      # 300ms pour les pointillés courts
        # self._pointille_delay = 0.8    # 800ms pour les pointillés longs
        # self._pointille_delay = 0.1    # 100ms pour les pointillés très courts
        self._last_line_time = time.time()  # Dernière fois qu'on a vu la ligne

    def start(self):
         """
         Active le mode de suivi de ligne du robot.
         Ceci démarrera la boucle de traitement de ligne du LineTracker
         """
         self.robot.move_robot(0)
         self.robot.change_direction(90)
         self.robot.pan_servo.set_angle(90)
         time.sleep(0.1)

    def update(self):
        current_time = time.time()
        status = self.robot.line_tracker.read_sensors()
        left = status['left']
        middle = status['middle']
        right = status['right']

        robot_speed = 25
        acceleration_rate = 150 
        turn_angle_left = 37  
        turn_angle_right = -37 
        print("left: {left}   middle: {middle}   right: {right}".format(**status))

        # Vérifier les obstacles
        if self.robot.ultra.get_distance_cm() < 40:
            print("[Obstacle] Obstacle détecté, changement de mode...")
            self.robot.motor.smooth_speed_and_wait(0)
            return

        # Détecter si on voit la ligne (au moins un capteur actif)
        line_detected = left == 1 or middle == 1 or right == 1
        
        if line_detected:
            # On voit la ligne, remettre à zéro les timers
            self._white_detected_time = None
            self._last_line_time = current_time
            
            # Logique normale de suivi de ligne
            if middle == 1:
                if self._previous_middle == 0:
                    self.robot.motor.smooth_speed_and_wait(0, acceleration_rate)

                if left == 0 and right == 1:
                    print("Adjusting right (line slightly left)")
                    angle = map_range(turn_angle_right, -98, 82, 0, 180)
                    self.robot.change_direction(angle)
                    self.robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate) 
                elif left == 1 and right == 0: 
                    print("Adjusting left (line slightly right)")
                    angle = map_range(turn_angle_left, -98, 82, 0, 180)
                    self.robot.change_direction(angle)
                    self.robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)
                else: 
                    angle = map_range(0, -98, 82, 0, 180)
                    self.robot.change_direction(angle)
                    print("Going straight (middle detected)")
                    self.robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)
            else:
                # Ligne détectée sur les côtés seulement
                if self._previous_middle == 1:
                    self.robot.motor.smooth_speed_and_wait(0, acceleration_rate)
                    
                if left == 1:
                    print("Turning left to find line")
                    angle = map_range(turn_angle_right, -98, 82, 0, 180)
                    self.robot.change_direction(angle)
                    self.robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate)
                elif right == 1: 
                    print("Turning right to find line")
                    angle = map_range(turn_angle_left, -98, 82, 0, 180)
                    self.robot.change_direction(angle)
                    self.robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate)
        else:
            # Aucune ligne détectée (tout blanc)
            if self._white_detected_time is None:
                # Premier moment où on détecte du blanc
                self._white_detected_time = current_time
                print(f"[Pointillé] Blanc détecté, attente de {self._pointille_delay}s...")
                
                # Continuer avec la dernière direction connue pendant un court moment
                print("Continuing with last direction...")
                self.robot.motor.smooth_speed(robot_speed // 2, acceleration=acceleration_rate)
                
            elif current_time - self._white_detected_time >= self._pointille_delay:
                # Le blanc persiste depuis plus de _pointille_delay secondes
                print("[Fin de ligne] Blanc persistant, fin de ligne détectée")
                print("NOOOO we lost the line :(")
                self.robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate)
            else:
                # On est dans la période d'attente, continuer doucement
                remaining_time = self._pointille_delay - (current_time - self._white_detected_time)
                print(f"[Pointillé] Attente... {remaining_time:.1f}s restantes")
                # Continuer lentement dans la même direction
                self.robot.motor.smooth_speed(robot_speed // 3, acceleration=acceleration_rate)

        self._previous_middle = middle
       
    def on_stop(self):
        super().on_stop()
        self.robot.line_tracker.shutdown()

    def avoid_obstacle(self): #à integrer dans une fonction qui switch entre modes line tracking et mode esquive obstacle
        seuil_obstacle = 40  # cm
        trop_proche = 20     # cm
        vitesse = 40

        print("[Obstacle] Démarrage du contournement...")

        # Étape 1 : roue à gauche, tête tout droit
        angle = 30
        angle = map_range(angle, -103, 77, 0, 180)
        self.robot.change_direction(angle)  # Tourne les roues à gauche (ajuste selon ton servo)
        self.robot.pan_servo.set_angle(90)         # Tête vers l’avant
        time.sleep(0.25) # Attendre que le servo se positionne
        dist = self.robot.ultra.get_distance_cm()
        # Étape 2 : tant que l’obstacle est devant, avancer et vérifier la proximité
        previous_state = 0
        state = 0
        while dist < seuil_obstacle:
            if dist < trop_proche:
                state = 1
                print("[Obstacle] Trop proche ! Manœuvre de recul...")
                if previous_state == 0:
                    self.robot.motor.smooth_speed_and_wait(0)
                    angle = -30
                    angle = map_range(angle, -103, 77, 0, 180)
                    self.robot.change_direction(angle)  # Tourne les roues à gauche (ajuste selon ton servo)
                
                self.robot.motor.smooth_speed(-vitesse)
            else:
                state = 0
                if previous_state == 1:
                    self.robot.motor.smooth_speed_and_wait(0)
                    angle = 30
                    angle = map_range(angle, -103, 77, 0, 180)
                    self.robot.change_direction(angle)
                
                self.robot.motor.smooth_speed(vitesse) 
            
            previous_state = state
            time.sleep(0.1)
            dist = self.robot.ultra.get_distance_cm()
            print("distance =", dist)

        self.robot.motor.smooth_speed_and_wait(0, acceleration=150)  # Stop the robot before proceeding

        # Étape 3 : roue droite pour se réaligner
        angle = 0
        angle = map_range(angle, -103, 77, 0, 180)
        self.robot.change_direction(angle)  # Roues droites

        # Étape 4 : scan pour détecter l’angle avec la plus grande distance
        result = radar_scan(self.robot)
        min_angle, max_angle = result.get_nearest_obstacle_limits()
        print("nearest obstacle : ", min_angle, max_angle)
        self.robot.pan_servo.set_angle((min_angle + max_angle) / 2)
        time.sleep(0.25) # Attendre que le servo se positionne
        # Cherche l’angle médian de l’objet (zone avec les distances les plus courtes)
       
        # Étape 5 : avancer jusqu’à ce que l’obstacle ait disparu du champ de vision
        obstacle_distance = self.robot.ultra.get_distance_cm() + 5 # On ajoute une marge de sécurité
        print("going until distance over :", obstacle_distance)
        while True:
            self.robot.motor.smooth_speed(vitesse)
            distance = self.robot.ultra.get_distance_cm()
            print("distance =", dist)
            if distance > obstacle_distance:
                break
            time.sleep(0.1)

        self.robot.motor.smooth_speed(0)

        # Étape 6 : tourner à droite pour revenir vers l’axe de la ligne
        angle = -15
        angle = map_range(angle, -103, 77, 0, 180)
        self.robot.change_direction(angle)  # Tourne à droite
        self.robot.motor.smooth_speed(vitesse)
        time.sleep(2)  # durée à ajuster selon l’environnement

        self.robot.motor.smooth_speed(0)
        angle = 0
        angle = map_range(angle, -103, 77, 0, 180)
        self.robot.change_direction(angle)  # Roue droite
        self.robot.pan_servo.set_angle(90)

        print("[Obstacle] Contournement terminé. Reprise du suivi de ligne.")
        return False

