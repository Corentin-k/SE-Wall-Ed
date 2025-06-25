import threading
import time
from robot.controller import Controller
from robot.radar_scan_utils import *

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

    def start(self):
         """
         Active le mode de suivi de ligne du robot.
         Ceci démarrera la boucle de traitement de ligne du LineTracker
         """
         self.robot.move_robot(0)
         self.robot.change_direction(90)
         time.sleep(0.1)

    def update(self):
        status = self.robot.line_tracker.read_sensors()
        left = status['left']
        middle = status['middle']
        right = status['right']

        robot_speed = 25
        acceleration_rate = 150 
        turn_angle_left = 37  
        turn_angle_right = -37 
        print("left: {left}   middle: {middle}   right: {right}".format(**status))

        if middle == 1:
            if self._previous_middle == 0:
                self.robot.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward

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
            if self._previous_middle == 1:
                self.robot.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward
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
                print("NOOOO we lost the line :(")
                self.robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate) 

        self._previous_middle = middle
    
    def on_stop(self):
        super().on_stop()
        self.robot.line_tracker.destroy()

    def avoid_obstacle(self): #à integrer dans une fonction qui switch entre modes line tracking et mode esquive obstacle
        seuil_obstacle = 30  # cm
        trop_proche = 10     # cm
        vitesse = 40

        print("[Obstacle] Démarrage du contournement...")

        # Étape 1 : roue à gauche, tête tout droit
        self.motor_servomotor.set_angle(30)  # Tourne les roues à gauche (ajuste selon ton servo)
        self.pan_servo.set_angle(90)         # Tête vers l’avant

        # Étape 2 : tant que l’obstacle est devant, avancer et vérifier la proximité
        while self.ultra.get_distance_cm() < seuil_obstacle:
            self.motor.smooth_speed(vitesse)
            dist = self.ultra.get_distance_cm()
            if dist < trop_proche:
                print("[Obstacle] Trop proche ! Manœuvre de recul...")
                self.motor.smooth_speed(-vitesse)
                time.sleep(0.5)
                self.motor.smooth_speed(0)
            time.sleep(0.1)

        self.motor.smooth_speed(0)

        # Étape 3 : roue droite pour se réaligner
        self.motor_servomotor.set_angle(90)  # Roues droites

        # Étape 4 : scan pour détecter l’angle avec la plus grande distance
       
        # radarScan(robot)
        # scan_data = robot.result  # [(angle, distance), ...]
        # if not scan_data:
        #     print("[Obstacle] Aucune donnée de scan.")
        #     return

        # Cherche l’angle médian de l’objet (zone avec les distances les plus courtes)
        # objet_zone = [data for data in scan_data if data[1] < seuil_obstacle]
        # if not objet_zone:
        #     print("[Obstacle] Aucun objet trouvé.")
        #     return
        Scan = ScanResult
        angles_min, angle_max = Scan.get_nearest_obstacle_limits()
        angle_milieu = angle_max - angles_min
        self.pan_servo.set_angle(angle_milieu)

        # Étape 5 : avancer jusqu’à ce que l’obstacle ait disparu du champ de vision
        while True:
            self.motor.smooth_speed(vitesse)
            if self.ultra.get_distance_cm() > seuil_obstacle:
                break
            time.sleep(0.1)

        self.motor.smooth_speed(0)

        # Étape 6 : tourner à droite pour revenir vers l’axe de la ligne
        self.motor_servomotor.set_angle(150)  # Tourne à droite
        self.motor.smooth_speed(vitesse)
        time.sleep(0.6)  # durée à ajuster selon l’environnement

        self.motor.smooth_speed(0)
        self.motor_servomotor.set_angle(90)  # Roue droite

        print("[Obstacle] Contournement terminé. Reprise du suivi de ligne.")
        return False
