import threading
import time
from robot.controller import Controller
from robot.radar_scan_utils import *

# def map_range(x, in_min, in_max, out_min, out_max):
#     return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

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

        self.last_line_detected = None  # right or left
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
        if self.robot.ultra.get_distance_cm() < 40:
            print("[Obstacle] Obstacle détecté, changement de mode...")
            self.robot.motor.smooth_speed_and_wait(0)
            self.avoid_obstacle(-1)
        line_detected = left == 1 or middle == 1 or right == 1
        if line_detected:
            # On voit la ligne, remettre à zéro les timers
            self._white_detected_time = None
            self._last_line_time = current_time
            
            # Logique normale de suivi de ligne
            if middle == 1:
                if self._previous_middle == 0:
                    self.robot.motor.smooth_speed_and_wait(0)

                if left == 0 and right == 1:
                    print("Adjusting right (line slightly left)")
                    
                    self.robot.change_direction(turn_angle_right)
                    self.robot.motor.smooth_speed(robot_speed)
                elif left == 1 and right == 0: 
                    print("Adjusting left (line slightly right)")
                    
                    self.robot.change_direction(turn_angle_left)
                    self.robot.motor.smooth_speed(robot_speed)
                else: 
                  
                    self.robot.change_direction(0)
                    print("Going straight (middle detected)")
                    self.robot.motor.smooth_speed(robot_speed)
            else:
                # Ligne détectée sur les côtés seulement
                if self._previous_middle == 1:
                    self.robot.motor.smooth_speed_and_wait(0)
                    
                if left == 1:
                    print("Turning left to find line")
                    #angle = map_range(turn_angle_right, -98, 82, 0, 180)
                    self.robot.change_direction(turn_angle_right)
                    self.robot.motor.smooth_speed(-robot_speed)
                elif right == 1: 
                    print("Turning right to find line")
                    #angle = map_range(turn_angle_left, -98, 82, 0, 180)
                    self.robot.change_direction(turn_angle_left)
                    self.robot.motor.smooth_speed(-robot_speed)
        else:
            # Aucune ligne détectée (tout blanc)
            if self._white_detected_time is None:
                # Premier moment où on détecte du blanc
                self._white_detected_time = current_time
                print(f"[Pointillé] Blanc détecté, attente de {self._pointille_delay}s...")
                
                # Continuer avec la dernière direction connue pendant un court moment
                print("Continuing with last direction...")
                self.robot.motor.smooth_speed(robot_speed)
                
            elif current_time - self._white_detected_time >= self._pointille_delay:
                # Le blanc persiste depuis plus de _pointille_delay secondes
                print("[Fin de ligne] Blanc persistant, fin de ligne détectée")
                self.robot.motor.smooth_speed(-robot_speed)
            else:
                # On est dans la période d'attente, continuer doucement
                remaining_time = self._pointille_delay - (current_time - self._white_detected_time)
                print(f"[Pointillé] Attente... {remaining_time:.1f}s restantes")
                # Continuer lentement dans la même direction
                self.robot.motor.smooth_speed(robot_speed)
        self._previous_middle = middle



    def bypass(self):
        """        Fonction pour contourner un obstacle détecté par le capteur ultrason.
        Elle gère le mouvement du robot pour éviter l'obstacle en tournant et en avançant.
        """
        pass  

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
    

