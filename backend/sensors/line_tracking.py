from gpiozero import InputDevice
import time 
# from motor         import Motors
# from servomotors import ServoMotors
class LineTracker:
    def __init__(self, pin_left=22, pin_middle=27, pin_right=17):
        
        self.sensor_left = InputDevice(pin=pin_left)
        self.sensor_middle = InputDevice(pin=pin_middle)
        self.sensor_right = InputDevice(pin=pin_right)
        # self.motors = Motors() 
        # self.wheel_servo = ServoMotors(channel=0)

    def read_sensors(self):
        
        return {
            'left': self.sensor_left.value,
            'middle': self.sensor_middle.value,
            'right': self.sensor_right.value
        }

    def print_status(self):
        
        status = self.read_sensors()
        print("left: {left}   middle: {middle}   right: {right}".format(**status))
    
    # def trackLineProcessing(self):
    #     status = self.read_sensors()
    #     left = status['left']
    #     middle = status['middle']
    #     right = status['right']

    #     robot_speed = 30 
    #     acceleration_rate = 50 
    #     turn_angle_left = 25  
    #     turn_angle_right = -25 
    #     straight_angle = 0  

    #     if middle == 0:
    #         if left == 0 and right == 1:
    #             print("Adjusting right (line slightly left)")
    #             self.wheel_servo.set_angle(90 + turn_angle_left) 
    #             self.motors.smooth_speed(robot_speed, acceleration=acceleration_rate) 
    #         elif left == 1 and right == 0: 
    #             print("Adjusting left (line slightly right)")
    #             self.wheel_servo.set_angle(90 + turn_angle_right) 
    #             self.motors.smooth_speed(robot_speed, acceleration=acceleration_rate)
    #         else: 
    #             print("Going straight (middle detected)")
    #             self.wheel_servo.set_angle(90 + straight_angle) 
    #             self.motors.smooth_speed(robot_speed, acceleration=acceleration_rate) 
    #     elif left == 0:
    #         print("Turning left to find line")
    #         self.wheel_servo.set_angle(90 + turn_angle_left) 
    #         self.motors.smooth_speed(robot_speed, acceleration=acceleration_rate)
    #     elif right == 0: 
    #         print("Turning right to find line")
    #         self.wheel_servo.set_angle(90 + turn_angle_right)
    #         self.motors.smooth_speed(robot_speed, acceleration=acceleration_rate) 
    #     else: 
    #         print("Searching for line (moving forward)")
    #         self.wheel_servo.set_angle(90 + straight_angle) 
    #         self.motors.smooth_speed(robot_speed, acceleration=acceleration_rate) 

    #     self.print_status() 
    #     time.sleep(0.1)

   
if __name__ == "__main__":
    tracker = LineTracker()
    # try:
    #     while True:
    #         tracker.trackLineProcessing()
    # except KeyboardInterrupt:
    #     print("Arrêt du robot.")
