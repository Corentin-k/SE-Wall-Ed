from gpiozero import InputDevice
import time

class LineTracker:
    def __init__(self, pin_left=22, pin_middle=27, pin_right=17):
        
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
    
    def trackLineProcessing(self):
        status = self.read_sensors()
        left = status['left']
        middle = status['middle']
        right = status['right']

        if middle == 0:
            scGear.moveAngle(0, 0)
            move.move(80, 1, "mid")
        elif left == 0:
            scGear.moveAngle(0, 30)
            move.move(80, 1, "left")
        elif right == 0:
            scGear.moveAngle(0, -30)
            move.move(80, 1, "right")
        else:
            move.move(0, 1, "no")

        print(left, middle, right)
        time.sleep(0.1)