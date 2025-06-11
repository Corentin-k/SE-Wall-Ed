import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import keyboard 

class ServoMotors:
    def __init__(self, pca_controller, channel, min_pulse=500, max_pulse=2400, actuation_range=180, initial_angle=90, step_size=2):
        """
        Initialise un objet ServoMotors pour contrôler un servo spécifique.
        Garde une trace de l'angle actuel et permet des mouvements par incréments.
        """
        self.pca = pca_controller 
        self.channel = channel
        self.servo = servo.Servo(self.pca.channels[channel], 
                                 min_pulse=min_pulse, 
                                 max_pulse=max_pulse,
                                 actuation_range=actuation_range)
        self.current_angle = initial_angle 
        self.step_size = step_size         
        self.set_angle(self.current_angle) 

    def set_angle(self, angle):
        """
        Définit l'angle du servo, en s'assurant qu'il reste dans les limites de 0 à 180 degrés.
        """
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        self.current_angle = angle 
        self.servo.angle = angle

    def move_increment(self, direction):
        """
        Déplace le servo d'un incrément (step_size) dans la direction spécifiée.
        direction: 1 pour augmenter l'angle, -1 pour diminuer l'angle.
        """
        new_angle = self.current_angle + (self.step_size * direction)
        self.set_angle(new_angle) 
    
    def stop(self):
        """
        Arrête le servo en le remettant à une position centrale (90 degrés).
        """
        self.set_angle(90)


    
def start_servos_control():
    i2c = busio.I2C(SCL, SDA)
    pca = PCA9685(i2c, address=0x5f) 
    pca.frequency = 50 

    PAN_CHANNEL = 1  
    TILT_CHANNEL = 2 
    
    pan_servo = ServoMotors(pca, channel=PAN_CHANNEL, initial_angle=90, step_size=2)
    tilt_servo = ServoMotors(pca, channel=TILT_CHANNEL, initial_angle=90, step_size=2)

    # Variables d'état pour suivre la direction de mouvement actuelle de chaque servo
    # 0 = arrêté, 1 = direction positive, -1 = direction négative
    current_pan_direction = 0
    current_tilt_direction = 0

    print("Contrôle des servos avec les touches A/D (Pan) et W/S (Tilt).")
    print("Appuyez sur 'Esc' pour quitter le programme.")

   
            
    new_pan_dir = 0 
    if keyboard.is_pressed('d'): # Si 'd' est appuyée, direction droite
        new_pan_dir = 1
    elif keyboard.is_pressed('a'): # Sinon, si 'a' est appuyée, direction gauche
        new_pan_dir = -1
    
    # Si la direction désirée pour le pan a changé, on la met à jour
    if new_pan_dir != current_pan_direction:
        current_pan_direction = new_pan_dir
    
    # Exécute le mouvement du pan si une direction est active 
    if current_pan_direction != 0:
        pan_servo.move_increment(current_pan_direction)


    new_tilt_dir = 0 
    if keyboard.is_pressed('w'): # Si 'w' est appuyée, direction haut
        new_tilt_dir = 1
    elif keyboard.is_pressed('s'): # Sinon, si 's' est appuyée, direction bas
        new_tilt_dir = -1
    
    # Si la direction désirée pour le tilt a changé, on la met à jour
    if new_tilt_dir != current_tilt_direction:
        current_tilt_direction = new_tilt_dir

    # Exécute le mouvement du tilt si une direction est active 
    if current_tilt_direction != 0:
        tilt_servo.move_increment(current_tilt_direction)

        
    
 


def start_servos_control():
    i2c = busio.I2C(SCL, SDA)
    pca = PCA9685(i2c, address=0x5f) 
    pca.frequency = 50 

    PAN_CHANNEL = 1  
    TILT_CHANNEL = 2 
    
    pan_servo = ServoMotors(pca, channel=PAN_CHANNEL, initial_angle=90, step_size=2)
    tilt_servo = ServoMotors(pca, channel=TILT_CHANNEL, initial_angle=90, step_size=2)

    # Variables d'état pour suivre la direction de mouvement actuelle de chaque servo
    # 0 = arrêté, 1 = direction positive, -1 = direction négative
    current_pan_direction = 0
    current_tilt_direction = 0

    print("Contrôle des servos avec les touches A/D (Pan) et W/S (Tilt).")
    print("Appuyez sur 'Esc' pour quitter le programme.")

    try:
        while True:
            # Vérifie si la touche 'Esc' est enfoncée pour quitter
            if keyboard.is_pressed('esc'): 
                break 
            
            new_pan_dir = 0 
            if keyboard.is_pressed('d'): # Si 'd' est appuyée, direction droite
                new_pan_dir = 1
            elif keyboard.is_pressed('a'): # Sinon, si 'a' est appuyée, direction gauche
                new_pan_dir = -1
            
            # Si la direction désirée pour le pan a changé, on la met à jour
            if new_pan_dir != current_pan_direction:
                current_pan_direction = new_pan_dir
            
            # Exécute le mouvement du pan si une direction est active 
            if current_pan_direction != 0:
                pan_servo.move_increment(current_pan_direction)


            new_tilt_dir = 0 
            if keyboard.is_pressed('w'): # Si 'w' est appuyée, direction haut
                new_tilt_dir = 1
            elif keyboard.is_pressed('s'): # Sinon, si 's' est appuyée, direction bas
                new_tilt_dir = -1
            
            # Si la direction désirée pour le tilt a changé, on la met à jour
            if new_tilt_dir != current_tilt_direction:
                current_tilt_direction = new_tilt_dir

            # Exécute le mouvement du tilt si une direction est active 
            if current_tilt_direction != 0:
                tilt_servo.move_increment(current_tilt_direction)

            time.sleep(0.05) # Petite pause pour contrôler la vitesse et réduire l'utilisation CPU

    except Exception as e:
        print(f"Erreur : {e}")
    
    finally:
        print("Arrêt des servos et nettoyage...")
        pan_servo.stop()
        tilt_servo.stop()
        keyboard.unhook_all() # Décroche tous les écouteurs du clavier pour une sortie propre
        print("Programme terminé.")

if __name__ == "__main__":
    start_servos_control()
