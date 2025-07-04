from gpiozero import InputDevice
import time 
from robot.config import line_pin_left, line_pin_middle, line_pin_right

class LineTracker:
    def __init__(self, pin_left=line_pin_left, pin_middle=line_pin_middle, pin_right=line_pin_right):
        
        self.sensor_left = InputDevice(pin=pin_left)
        self.sensor_middle = InputDevice(pin=pin_middle)
        self.sensor_right = InputDevice(pin=pin_right)
      
    def read_sensors(self):
        return {
            'left': self.sensor_left.value,
            'middle': self.sensor_middle.value,
            'right': self.sensor_right.value
        }

    def print_status(self):
        
        status = self.read_sensors()
        print("left: {left}   middle: {middle}   right: {right}".format(**status))
    def shutdown(self):
        self.sensor_left.close()
        self.sensor_middle.close()
        self.sensor_right.close()
   
if __name__ == "__main__":
    tracker = LineTracker()
    # try:
    #     while True:
    #         tracker.trackLineProcessing()
    # except KeyboardInterrupt:
    #     print("Arrêt du robot.")
