import threading
import time
from robot.controller import Controller

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
            Ceci démarrera la boucle de traitement de ligne du LineTracker.
            """
            self.robot.move_robot(0)
            self.robot.change_direction(90)
            time.sleep(0.1)
    
    def stop(self):
        self.robot.motor.smooth_speed(0)
        self.robot.motor_servomotor.set_angle(map_range(0, -98, 82, 0, 180))

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
