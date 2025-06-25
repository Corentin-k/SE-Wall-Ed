from sensors import *
from robot.config import *
import time
from robot.controller import Controller

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

class RadarController(Controller):
    def __init__(self, robot):
        super().__init__(robot)
        self.result = []

    def radar_scan(self):
            pwm0_min = 0
            pwm0_max = 180
            scan_speed = 2
            self.robot.pan_servo.set_angle(pwm0_min) 
            while pwm0_min < pwm0_max:
                self.robot.pan_servo.set_angle(pwm0_min + scan_speed) 
                dist = self.robot.ultra.get_distance_cm()
                self.result.append([dist, pwm0_min])
                pwm0_min = pwm0_min + scan_speed
            pwm0_min = 0
            while pwm0_max > pwm0_min:
                self.robot.pan_servo.set_angle(pwm0_max - scan_speed) 
                dist = self.robot.ultra.get_distance_cm()
                self.result.append([dist, pwm0_max])
                pwm0_max = pwm0_max - scan_speed
            self.robot.pan_servo.set_angle(90)

    def start(self):
        
        self.robot.motor_servomotor.set_angle(map_range(0, -98, 82, 0, 180))
        self.robot.tilt_servo.set_angle(90)
        self.robot.pan_servo.set_angle(90)

    def update(self):
        dist = self.robot.ultra.get_distance_cm()
        seuil= 30
        vitesse = 25
        while dist < seuil:   
            self.robot.motor.smooth_speed(0)
            time.sleep(0.5)
            self.radar_scan()
            if self.result:
                dist_max = max([item[0] for item in self.result])
                angle_max = max([item[1] for item in self.result if item[0] == dist_max])
                print(f" Direction choisie : {angle_max}°, Distance : {dist_max:.1f} cm")
                if angle_max < 90:
                    angle_max = map_range(37, -98, 82, 0, 180)
                    self.robot.motor_servomotor.set_angle(angle_max)
                    self.robot.pan_servo.set_angle(angle_max)
                else:
                    angle_max = map_range(-37, -98, 82, 0, 180)
                    self.robot.motor_servomotor.set_angle(angle_max)
                    self.robot.pan_servo.set_angle(angle_max)
                dist = seuil + 1
                self.robot.motor.smooth_speed(vitesse)
                time.sleep(1)
        self.robot.motor.smooth_speed(vitesse)
        dist = self.robot.ultra.get_distance_cm()
        print(f"Distance frontale : {dist:.1f} cm")

    def dist_redress(robot):
            mark = 0
            distValue = robot.ultra.get_distance_cm()
            while True:
                distValue = robot.ultra.get_distance_cm()
                if distValue > 900:
                    mark += 1
                elif mark > 5 or distValue < 900:
                    break
                print(distValue)
            return round(distValue, 2)
