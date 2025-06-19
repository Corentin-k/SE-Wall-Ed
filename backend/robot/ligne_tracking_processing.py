import threading
import time

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

def activate_line_tracking(robot):
        """
        Active le mode de suivi de ligne du robot.
        Ceci démarrera la boucle de traitement de ligne du LineTracker.
        """
        robot.move_robot(0)
        robot.change_direction(90)
        time.sleep(0.1)

        robot._line_tracking_running = True
        robot._line_tracking_thread = threading.Thread(target=run_line_tracking_loop, args=(robot,), daemon=True)
        robot._line_tracking_thread.start()


def run_line_tracking_loop(robot):
    """
    Boucle interne pour exécuter le traitement de suivi de ligne.
    """
    while robot._line_tracking_running:
        robot.trackLineProcessing()

def stop_line_tracking(robot):
    """
    Désactive le mode de suivi de ligne du robot.
    """
    robot._line_tracking_running = False
    if robot._line_tracking_thread and robot._line_tracking_thread.is_alive():
        robot._line_tracking_thread.join()
    robot.stop_robot()

def track_Line_processing(robot):
    status = robot.line_tracker.read_sensors()
    left = status['left']
    middle = status['middle']
    right = status['right']

    robot_speed = 25
    acceleration_rate = 150 
    turn_angle_left = 37  
    turn_angle_right = -37 
    print("left: {left}   middle: {middle}   right: {right}".format(**status))

    if middle == 1:
        if robot._previous_middle == 0:
            robot.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward

        if left == 0 and right == 1:
            print("Adjusting right (line slightly left)")
            angle = map_range(turn_angle_right, -98, 82, 0, 180)
            robot.change_direction(angle)
            robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate) 
        elif left == 1 and right == 0: 
            print("Adjusting left (line slightly right)")
            angle = map_range(turn_angle_left, -98, 82, 0, 180)
            robot.change_direction(angle)
            robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate)
        else: 
            angle = map_range(0, -98, 82, 0, 180)
            robot.change_direction(angle)
            print("Going straight (middle detected)")
            robot.motor.smooth_speed(robot_speed, acceleration=acceleration_rate) 
    else:
        if robot._previous_middle == 1:
            robot.motor.smooth_speed_and_wait(0, acceleration_rate) # stop the robot before going forward
        if left == 1:
            print("Turning left to find line")
            angle = map_range(turn_angle_right, -98, 82, 0, 180)
            robot.change_direction(angle)
            robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate)
        elif right == 1: 
            print("Turning right to find line")
            angle = map_range(turn_angle_left, -98, 82, 0, 180)
            robot.change_direction(angle)
            robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate) 
        else: 
            print("NOOOO we lost the line :(")
            robot.motor.smooth_speed(-robot_speed, acceleration=acceleration_rate) 

    robot._previous_middle = middle