from sensors.motor2 import Motor
from sensors import *
from robot.config import *

motor = Motor()

def set_motor_speed(speed):
    motor.set_speed(speed)
    return f"Speed set to {speed}"

def stop_motor():
    motor.stop()
    return "Motor stopped"


   def automaticProcessing(self):
		print('automaticProcessing')
		dist = self.distRedress()
		print(dist, "cm")
		if dist >= 50:			# More than 50CM, go straight.
            self.motor_servomotor.set_angle(0,0)
			time.sleep(0.3)
            self.motor.smooth_speed(40)
			print("Forward")
		# More than 30cm and less than 50cm, detect the distance between the left and right sides.
		elif dist > 30 and dist < 50:
            self.motor.smooth_speed(0)
            self.motor_servomotor.set_angle(1, -40)
			time.sleep(0.4)
			distLeft = self.distRedress()
			self.scanList[0] = distLeft

			# Go in the direction where the detection distance is greater.
            self.motor_servomotor.set_angle(1, 40)
			time.sleep(0.4)
			distRight = self.distRedress()
			self.scanList[1] = distRight
			print(self.scanList)
            self.motor_servomotor.set_angle(1, 0)
			if self.scanList[0] >= self.scanList[1]:
                self.motor_servomotor.set_angle(0, -30)
				time.sleep(0.3)
                self.motor.smooth_speed(40)
				print("Left")
			else:
                self.motor_servomotor.set_angle(0, 30)
				time.sleep(0.3)
                self.motor.smooth_speed(40, 1)
				print("Right")
		else:		# The distance is less than 30cm, back.
            self.motor_servomotor.set_angle(0, 0)
			time.sleep(0.3)
            self.motor.smooth_speed(-40)
			print("Back")
		time.sleep(0.4)