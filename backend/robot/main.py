import threading
import time
import logging
from sensors import *
from robot.config import *
import asyncio

logger = logging.getLogger(__name__)

def map_range(x,in_min,in_max,out_min,out_max):
        return (x - in_min)/(in_max - in_min) *(out_max - out_min) +out_min

class Robot:
    def __init__(self):
        # Initialisation des composants
        self.camera = Camera()
        self.ultra = UltrasonicSensor()

        self.init_servo_head()
        self.init_movement()
        self.init_leds()
        self.buzzer = Buzzer()
        self.line_tracker = LineTracker(
            pin_left=line_pin_left,
            pin_middle=line_pin_middle,
            pin_right=line_pin_right
        )
        # Variables pour le pilotage de la tête
        self._pan = 0
        self._tilt = 0
        self._head_running = True
        self._head_lock = threading.Lock()

        # Centrage initial de la tête
        self.move_head(0, 0)

        # Lancement du thread de mouvement de la tête
        self._head_thread = threading.Thread(target=self._head_loop, daemon=True)
        self._head_thread.start()

        #Utils variables for line tracking
        self._previous_middle = 0

        logger.info("Robot initialized")

    # -------------------- Initialisation des composants -------------------

    def init_servo_head(self):
        self.pan_servo = ServoMotors(channel=PAN_CHANNEL, initial_angle=90, step_size=2)
        self.tilt_servo = ServoMotors(channel=TILT_CHANNEL, initial_angle=90, step_size=2)

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

    # -------------------- Méthodes de contrôle du robot -------------------

    def led(self, hex_color):
        self.leds.set_color_hex(hex_color)

    def get_camera_frame(self):
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
        # Sur shutdown, recentre la tête
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

    def shutdown(self):
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
        #self.leds.start_police(interval=0.3)
        self.ws2812.police()
        threading.Thread(target=self.buzzer.play_tune, args=("Police",), daemon=True).start()

    def stop_police(self):
        # Arrête le buzzer
        self.buzzer.stop()
        self.ws2812.led_close()
        self.leds.stop_police()

    def shutdown(self): # Note: There are two shutdown methods. This one will override the first.
        """
        Nettoie les ressources du robot.
        """
        self.camera.destroy()
        self.buzzer.stop()
        self.pan_servo.stop()
        self.tilt_servo.stop()
        self.motor_servomotor.stop()
        self.ws2812.led_close()
        self.leds.destroy()

    def radarScan(self):
        pwm0_min = -90
        pwm0_max = 90

        scan_speed = 1
        result = []
        pwm0_pos = pwm0_max
        self.motor_servomotor.set_angle(0) # Assuming this means set angle for a specific servo or axis
        time.sleep(0.8)
        while pwm0_pos > pwm0_min:
            pwm0_pos -= scan_speed
            self.motor_servomotor.set_angle(1, pwm0_pos) # Assuming this means set angle for a specific servo or axis
            dist = self.ultra.get_distance_cm()
            if dist > 20:
                continue
            theta = 90 - pwm0_pos
            result.append([dist, theta])
            time.sleep(0.02)
        self.motor_servomotor.set_angle(0) # Corrected from self.motor_servomotor.self(1, 0) - assuming it resets an angle
        return result

    def distRedress(self):
        mark = 0
        distValue = self.ultra.get_distance_cm()
        while True:
            distValue = self.ultra.get_distance_cm() # Corrected from ultra.checkdist() assuming ultra is self.ultra
            if distValue > 900:
                mark += 1
            elif mark > 5 or distValue < 900:
                break
            print(distValue)
        return round(distValue, 2)

    def start_line_tracking(self):
        """
        Active le mode de suivi de ligne du robot.
        Ceci démarrera la boucle de traitement de ligne du LineTracker.
        """
        logger.info("Starting line tracking mode.")
        self.move_robot(0)
        self.change_direction(90)
        time.sleep(0.1)

        self._line_tracking_running = True
        self._line_tracking_thread = threading.Thread(target=self._run_line_tracking_loop, daemon=True)
        self._line_tracking_thread.start()


    def _run_line_tracking_loop(self):
        """
        Boucle interne pour exécuter le traitement de suivi de ligne.
        """
        while self._line_tracking_running:
            self.trackLineProcessing()

    def stop_line_tracking(self):
        """
        Désactive le mode de suivi de ligne du robot.
        """
        logger.info("Stopping line tracking mode.")
        self._line_tracking_running = False
        if self._line_tracking_thread and self._line_tracking_thread.is_alive():
            self._line_tracking_thread.join()
        self.stop_robot()

    def trackLineProcessing(self):
        status = self.line_tracker.read_sensors()
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
                self.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward

            if left == 0 and right == 1:
                print("Adjusting right (line slightly left)")
                angle = map_range(turn_angle_right, -98, 82, 0, 180)
                self.change_direction(angle)
                self.motor.smooth_speed(robot_speed, acceleration=acceleration_rate) 
            elif left == 1 and right == 0: 
                print("Adjusting left (line slightly right)")
                angle = map_range(turn_angle_left, -98, 82, 0, 180)
                self.change_direction(angle)
                self.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)
            else: 
                angle = map_range(0, -98, 82, 0, 180)
                self.change_direction(angle)
                print("Going straight (middle detected)")
                self.motor.smooth_speed(robot_speed, acceleration=acceleration_rate) 
        else:
            if self._previous_middle == 1:
                self.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward
            if left == 1:
                print("Turning left to find line")
                angle = map_range(turn_angle_right, -98, 82, 0, 180)
                self.change_direction(angle)
                self.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate)
            elif right == 1: 
                print("Turning right to find line")
                angle = map_range(turn_angle_left, -98, 82, 0, 180)
                self.change_direction(angle)
                self.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate) 
            else: 
                print("NOOOO we lost the line :(")
                # self.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward
                self.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate) 

        self._previous_middle = middle
        # Assuming print_status() is a method of the Robot class, otherwise it needs to be defined
        # self.print_status() 
        # time.sleep(0.1)

    def stop_robot(self):
        """
        Arrête les moteurs et réinitialise les servos à leur position centrale.
        """
        print("Stopping motors and resetting servos...")
        self.motor.smooth_speed(0)
        self.motor_servomotor.set_angle(90)
        time.sleep(0.5)

    def automaticProcessing2(self):
        print('automaticProcessing')
        self.stop_robot()
        dist = self.distRedress()
        print(dist, "cm")
        if dist >= 50:                  # More than 50CM, go straight.
            self.motor_servomotor.set_angle(90)
            time.sleep(0.3)
            self.motor.smooth_speed(40)
            print("Forward")
                # More than 30cm and less than 50cm, detect the distance between the left and right sides.
        elif dist > 30 and dist < 50:
            self.motor.smooth_speed(0)
            self.motor_servomotor.set_angle(0)
            time.sleep(0.4)
            distLeft = self.distRedress()
            self.scanList[0] = distLeft

                        # Go in the direction where the detection distance is greater.
            self.motor_servomotor.set_angle(130)
            time.sleep(0.4)
            distRight = self.distRedress()
            self.scanList[1] = distRight
            print(self.scanList)
            self.motor_servomotor.set_angle(90)
            if self.scanList[0] >= self.scanList[1]:
                self.motor_servomotor.set_angle(-30)
                time.sleep(0.3)
                self.motor.smooth_speed(40)
                print("Left")
            else:
                self.motor_servomotor.set_angle(120)
                time.sleep(0.3)
                self.motor.smooth_speed(40, 1)
                print("Right")
        else:           # The distance is less than 30cm, back.
            self.motor_servomotor.set_angle(90)
            time.sleep(0.3)
            self.motor.smooth_speed(-40)
            print("Back")
        time.sleep(0.4)
    def automaticProcessing(self):
        print('automaticProcessing')
        self.stop_robot()
        dist = self.distRedress()
        print(dist, "cm")
        if dist >= 50:                  # More than 50CM, go straight.
            self.motor_servomotor.set_angle(92)
            self.motor.smooth_speed(40)
            print("Forward")
                # More than 30cm and less than 50cm, detect the distance between the left and right sides.
        elif dist > 30 and dist < 50:
            self.motor.smooth_speed(0)
    
            self.motor_servomotor.set_angle(92)

            self.pan_servo.set_angle(180)
            time.sleep(0.4)
            distLeft = self.distRedress()
            self.scanList[0] = distLeft

                        # Go in the direction where the detection distance is greater.
            self.pan_servo.set_angle(0)
            time.sleep(0.4)
            distRight = self.distRedress()
            self.scanList[1] = distRight
            print(self.scanList)
            if self.scanList[0] >= self.scanList[1]:
                self.motor_servomotor.set_angle(58)
                self.motor.smooth_speed(40)
                print("Left")
            else:
                self.motor_servomotor.set_angle(118)
                self.motor.smooth_speed(40)
                print("Right")
        else:           # The distance is less than 30cm, back.
            self.motor_servomotor.set_angle(92)
            self.motor.smooth_speed(-40)
            print("Back")
        time.sleep(0.4)
