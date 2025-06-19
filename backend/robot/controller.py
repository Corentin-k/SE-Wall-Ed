from sensors import *
from robot.config import *
import time
def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min



def radar_scan(robot):
        pwm0_min = 0
        pwm0_max = 180
        scan_speed = 2
        robot.pan_servo.set_angle(pwm0_min) 
        while pwm0_min < pwm0_max:
            robot.pan_servo.set_angle(pwm0_min + scan_speed) 
            dist = robot.ultra.get_distance_cm()
            robot.result.append([dist, pwm0_min])
            pwm0_min = pwm0_min + scan_speed
            # if dist > 20:
            #       robot.motor.smooth_speed(0)     
                  # reculer en pwm0_min
        # if robot.result:
        #        min_dist_first_loop = min([item[0] for item in robot.result])
               #print(f"Minimum distance after first scan: {min_dist_first_loop} cm")
        pwm0_min = 0
        while pwm0_max > pwm0_min:
            robot.pan_servo.set_angle(pwm0_max - scan_speed) 
            dist = robot.ultra.get_distance_cm()
            robot.result.append([dist, pwm0_max])
            pwm0_max = pwm0_max - scan_speed
        robot.pan_servo.set_angle(90)

            # if dist > 20:
            #       robot.motor.smooth_speed(0)     
                  # reculer en pwm0_min
        # if robot.result:
            #    min_dist_second_loop = min([item[0] for item in robot.result])
            # #    print(f"Minimum distance after second scan: {min_dist_second_loop} cm")
            #     max([item[0] for item in robot.result])
		

def automatic_processing(robot):
    #while True:
        #radarScan(robot)
    #pass
    print('automaticProcessing')
    seuil= 20
    vitesse = 15
    robot.motor_servomotor.set_angle(90)
    robot.pan_servo.set_angle(90)
    robot.motor.smooth_speed(vitesse)
    dist = robot.ultra.get_distance_cm()
    print(f"Distance frontale : {dist:.1f} cm")
    if dist < seuil:
        robot.motor.smooth_speed(0)
        print(dist, "cm")
        radar_scan(robot)
        if robot.result:
            dist_max = max([item[0] for item in robot.result])
            angle_max = max([item[1] for item in robot.result if item[0] == dist_max])
            print(f" Direction choisie : {angle_max}°, Distance : {dist_max:.1f} cm")
            robot.motor_servomotor.set_angle(angle_max)
        else:
            print(" Aucun espace dégagé détecté.")
    robot.motor.smooth_speed(vitesse)

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