import time
from board import SCL, SDA
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
import keyboard 

class ServoMotors:
    def __init__(self, channel, min_pulse=500, max_pulse=2400, actuation_range=180, initial_angle=90, step_size=2):
        """
        Initialise un objet ServoMotors pour contrôler un servo spécifique.
        Garde une trace de l'angle actuel et permet des mouvements par incréments.
        """
        i2c = busio.I2C(SCL, SDA)
        self.pca = PCA9685(i2c, address=0x5f) 
        self.pca.frequency = 50 


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
        #if self.channel == 0:
         #  if angle < 73:
          #       angle = 73
           # elif angle > 118:
            #     angle = 118
        self.current_angle = angle 
        self.servo.angle = angle

    def move_increment(self, direction):
        """
        Déplace le servo d'un incrément (step_size) dans la direction spécifiée.
        direction: 1 pour augmenter l'angle, -1 pour diminuer l'angle.
        """
        new_angle = self.current_angle + (self.step_size * direction)
        self.set_angle(new_angle) 
    
    def shutdown(self):
        """
        Arrête le servo en le remettant à une position centrale (90 degrés).
        """
        self.set_angle(90)
        #self.servo.set_pulse_width(None)
        self.pca.channels[self.channel].duty_cycle = 0

def start_servos_control():
   
    PAN_CHANNEL = 1  
    TILT_CHANNEL = 2 
    WHEEL_CHANNEL = 0
    
    pan_servo = ServoMotors(channel=PAN_CHANNEL)
    tilt_servo = ServoMotors(channel=TILT_CHANNEL)
    wheel_servo = ServoMotors(channel=WHEEL_CHANNEL)

    # Variables d'état pour suivre la direction de mouvement actuelle de chaque servo
    # 0 = arrêté, 1 = direction positive, -1 = direction négative
    current_pan_direction = 0
    current_tilt_direction = 0
    current_wheel_direction = 0

    print("Appuyez sur 'Esc' pour quitter le programme.")

    try:
        c = 90
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

            # Vérifie la direction des roues
            new_wheel_dir = 0
            if (keyboard.is_pressed('t') and c <= 118):
                new_wheel_dir = 1
                c += 1
                print(c)

            elif (keyboard.is_pressed('y') and c >= 73):
                new_wheel_dir = -1
                c -= 1
                print(c) 

            if new_wheel_dir != current_wheel_direction:
                current_wheel_direction = new_wheel_dir
                print(f"Wheel direction changed to: {current_wheel_direction}") 

            if current_wheel_direction != 0:
                wheel_servo.move_increment(current_wheel_direction)

            time.sleep(0.05) # Petite pause pour contrôler la vitesse et réduire l'utilisation CPU

    except Exception as e:
        print(f"Erreur : {e}")
    
    finally:
        print("Arrêt des servos et nettoyage...")
        pan_servo.stop()
        tilt_servo.stop()
        keyboard.unhook_all() # Décroche tous les écouteurs du clavier pour une sortie propre
        print("Programme terminé.")

def servo_test():
    PAN_CHANNEL = 1  
    TILT_CHANNEL = 2 
    WHEEL_CHANNEL = 0
    
    pan_servo = ServoMotors(channel=PAN_CHANNEL)
    tilt_servo = ServoMotors(channel=TILT_CHANNEL)
    wheel_servo = ServoMotors(channel=WHEEL_CHANNEL)

    pan_servo.set_angle(20)
    tilt_servo.set_angle(20)
    wheel_servo.set_angle(90)
    time.sleep(1)

    for i in range(400, 200, -10):
        print("moving in ", i, "ms")
        pan_servo.set_angle(170)
        tilt_servo.set_angle(170)
        time.sleep(i / 1000.0)
        pan_servo.set_angle(20)
        tilt_servo.set_angle(20)
        time.sleep(i / 1000.0)

if __name__ == "__main__":
    # start_servos_control()
    servo_test()
