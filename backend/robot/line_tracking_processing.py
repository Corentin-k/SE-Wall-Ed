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
        self.last_line_detected = None  # right or left
        self._performing_right_angle = False 
        self._lost_counter = 0
        self._lost_threshold = 3
        self._reverse_duration = 1.2  # Durée en secondes pour reculer fort
        self._lost_delay = 0.25  # Délai en secondes avant d'incrémenter lost_counter
        self._last_lost_time = None  # Temps de la première détection de perte de ligne
        self._last_line_detected = 0  # Dernière fois que la ligne a été détectée

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
        #print("[Suivi ligne] Mise à jour du suivi de ligne...")
        status = self.robot.line_tracker.read_sensors()
        left = status['left']
        middle = status['middle']
        right = status['right']
        robot_speed = 40
        acceleration_rate = 350
        turn_angle_left = 30
        turn_angle_right = -30

        if self.robot.ultra.get_distance_cm() < 37:
            self.robot.motor.smooth_speed_and_wait(0)
            self.avoid_obstacle2()

        if self._performing_right_angle:
            # Si on est déjà en train de chercher la ligne, ne pas interférer
            return

        if left == 0 and middle == 0 and right == 0:
            # Pas de ligne détectée
            current_time = time.time()
            
            # Si c'est la première fois qu'on perd la ligne, initialiser le temps
            if self._last_lost_time is None:
                self._last_lost_time = current_time
                print("[Suivi ligne] Ligne perdue - début du délai d'attente")
                return
            
            # Vérifier si le délai d'attente est écoulé avant d'incrémenter
            if current_time - self._last_lost_time >= self._lost_delay:
                self._lost_counter += 1
                #print(f"[Suivi ligne] Ligne perdue ({self._lost_counter}/{self._lost_threshold})")
                
                # Réinitialiser le temps pour le prochain incrément
                self._last_lost_time = current_time

                if self._lost_counter >= self._lost_threshold:
                    #print("[Suivi ligne] Seuil de perte atteint, déclenchement de la recherche")
                    self.robot.motor.smooth_speed(0)
                    self._performing_right_angle = True
                    self._lost_counter = 0
                    self._last_lost_time = None  # Reset du temps de perte
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


        #print("left: {left}   middle: {middle}   right: {right}".format(**status))
        status = self.robot.line_tracker.read_sensors()
        left = status['left']
        middle = status['middle']
        right = status['right']
        #print("left: {left}   middle: {middle}   right: {right}".format(**status))
        if middle == 1:
            print("REPRISSSSSSSSSSSSSSSe")
            if self._previous_middle == 0:
                self.robot.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward
            if left == 0 and right == 1:
                #print("Adjusting right (line slightly left)")
                self.robot.change_direction(turn_angle_right+10)
                self.robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)
            elif left == 1 and right == 0:
                #print("Adjusting left (line slightly right)")
                self.robot.change_direction(turn_angle_left-10)
                self.robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)
            else:
                self.robot.change_direction(0)
                #print("Going straight (middle detected)")
                self.robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)
        else:
            if self._previous_middle == 1:
                self.robot.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward
            if left == 1:
                #print("Turning left to find line")
                self.robot.change_direction(turn_angle_right)
                self.robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate)
            elif right == 1:
                #print("Turning right to find line")
                self.robot.change_direction(turn_angle_left)
                self.robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate)
            else:
                #print("NOOOO we lost the line :(")
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
        
        self.robot.motor.smooth_speed_and_wait(0)
    
        self.robot.motor.smooth_speed(-35) 
        time.sleep(0.52) 
        self.robot.motor.smooth_speed_and_wait(0)  # Stopper le robot après le reculz
        # Étape 2: Avancer vers la gauche et chercher la ligne
        #print("[Recherche ligne] Étape 2: Recherche vers la gauche...")
        self.robot.change_direction(-30)  # Tourner à gauche
        time.sleep(0.2)  # Laisser le temps de positionner les roues

        # Avancer en cherchant la ligne
        self.robot.motor.smooth_speed(35) 
        search_start = time.time()
        time_rotate_start= time.time()
        line_found = False
        self._last_line_detected = time.time()
        while time.time() - search_start < 3:  # Timeout de 3 secondes
            sensors = self.robot.line_tracker.read_sensors()
            if (sensors['middle'] == 1 or sensors['left'] == 1 or sensors['right'] == 1) and time.time() - self._last_line_detected > 1.5:
                #print("[Recherche ligne] ✓ Ligne retrouvée vers la gauche!")
                self.robot.motor.smooth_speed_and_wait(0)
                self.robot.change_direction(0)  # Remettre direction droite
                time.sleep(0.3)
                self._performing_right_angle = False
                line_found = True
                
                return
            time.sleep(0.05)  # Vérification fréquente
        time_rotate_stop = time.time()
        time_roate= time_rotate_stop - time_rotate_start
        self.robot.motor.smooth_speed_and_wait(0)
        time.sleep(0.9)  # Pause pour stabiliser avant de changer de direction

        
        # Étape 3: Si pas trouvé à gauche, arrêter et reculer
        if not line_found:
            #print("[Recherche ligne] Ligne non trouvée à gauche, recul...")
            # Reculer dans la même direction (toujours tourné à gauche)
            self.robot.motor.smooth_speed(-35)
            print("[Recherche ligne] Étape 3: Recul dans la même direction...")
            time.sleep(time_roate-0.3)  # Reculer suffisamment
            self.robot.motor.smooth_speed_and_wait(0)

            # Étape 4: Tourner vers la droite et chercher
            #print("[Recherche ligne] z 4: Recherche vers la droite...")    
            self.robot.change_direction(30)  # Tourner à droite
            time.sleep(0.2)  # Laisser le temps de positionner les roues
            # Avancer vers la droite en cherchant
            self.robot.motor.smooth_speed(35) 
            search_start = time.time()
            line_found = False
            self._last_line_detected = time.time()
            while time.time() - search_start < 3:  # Timeout de 3 secondes
                sensors = self.robot.line_tracker.read_sensors()
                if (sensors['middle'] == 1 or sensors['left'] == 1 or sensors['right'] == 1) and time.time() - self._last_line_detected > 1.5:
                    #print("[Recherche ligne] ✓ Ligne retrouvée vers la gauche!")
                    self.robot.motor.smooth_speed_and_wait(0)
                    self.robot.change_direction(0)  # Remettre direction droite
                    time.sleep(0.3)
                    self._performing_right_angle = False
                    line_found = True
                    return
                time.sleep(0.05)  # Vérification fréquente
            self.robot.motor.smooth_speed_and_wait(0)
            time.sleep(0.9)

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

    
    def avoid_obstacle2(self):
        vitesse = 35
        print("[Obstacle] Démarrage du contournement...")
        self.robot.motor.smooth_speed_and_wait(0, acceleration=150)
        # Etape 1 : repèrer la direction à prendre
        self.robot.pan_servo.set_angle(0)
        time.sleep(1)
        dist = self.robot.ultra.get_distance_cm()
        angle=0
        if dist < 30:
            angle = 30
        else:
            self.robot.pan_servo.set_angle(180)
            time.sleep(1)
            dist = self.robot.ultra.get_distance_cm()
            if dist < 30:
                angle = -30
            else:
                angle = 0
                time.sleep(1)
                self.robot.pan_servo.set_angle(90)
                return
        time.sleep(1)
        self.robot.pan_servo.set_angle(90)
        # Etape 2 : reculer légèrement pour braquer ensuite du bon côté
        time.sleep(1)
        self.robot.motor.smooth_speed(-vitesse, acceleration=150)
        time.sleep(0.9)
        self.robot.motor.smooth_speed_and_wait(0, acceleration=150)
        time.sleep(1)
        # Etape 3 : tourner à gauche ou à droite
        self.robot.change_direction(angle)
        # Etape 4 : avancer jusqu'à ce que l'on retrouve la ligne.
        self.robot.motor.smooth_speed(vitesse, acceleration=150) 
        time.sleep(1.5)
        self.robot.change_direction(-angle)
        while self.robot.line_tracker.read_sensors()['middle'] == 0:
            pass
        self.robot.motor.smooth_speed_and_wait(0, acceleration=150)
        self.robot.pan_servo.set_angle(90)

    


        

