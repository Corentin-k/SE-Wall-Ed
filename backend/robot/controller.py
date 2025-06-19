from sensors import *
from robot.config import *
import time
def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

def radarScan(robot):
    pwm0_min = 0
    pwm0_max = 180

    scan_speed = 1
    result = []
    pwm0_pos = pwm0_max
    robot.pan_servo.set_angle(pwm0_pos)
    time.sleep(0.8)
    while pwm0_pos > pwm0_min:
        pwm0_pos -= scan_speed
        robot.pan_servo.set_angle(pwm0_pos)
        dist = robot.ultra.get_distance_cm()
        result.append([dist, pwm0_pos])
        time.sleep(0.5)
    robot.pan_servo.set_angle(92)
    print(result)
    return result

def automaticProcessing(robot):
    print('automaticProcessing')
    robot.stop_robot()
    seuil= 30
    vitesse = 40
    try: 
        while True:
        
            dist = robot.ultra.get_distance_cm()
            if dist < seuil:
                robot.motor.smooth_speed(0)
                print(dist, "cm")
            else:
                robot.motor.smooth_speed(vitesse)
                scans = radarScan(robot)
                if not scans: #pas d'esapce
                    robot.motor.smooth_speed(-vitesse)
                    time.sleep(0.5)
                    robot.motor.smooth_speed(0)
                    continue
                angle_max, dist_max = max(scans, key=lambda x: x[1]) # Trouve la distance maximale
                robot.motor_servomotor.set_angle(mapped)
                robot.motor.smooth_speed(vitesse)


            time.sleep(0.1)
    finally:
        robot.motor.smooth_speed(0)
