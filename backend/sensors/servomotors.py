# import time
# from board import SCL, SDA
# import busio
# from adafruit_motor import servo
# from adafruit_pca9685 import PCA9685

# i2c = busio.I2C(SCL, SDA)
# # Create a simple PCA9685 class instance.
# pca = PCA9685(i2c, address=0x5f) 

# pca.frequency = 50

# # The pulse range is 750 - 2250 by default. This range typicall# range, but the default is to use 180 degrees. You can specify># servo7 = servo.Servo(pca.channels[7], actuation_range=135)
# def set_angle(ID, angle):
#     servo_angle = servo.Servo(pca.channels[ID], min_pulse=500, max_pulse=2400,actuation_range=180)
#     servo_angle.angle = angle

# def test(channel):
#     for i in range(180): # The servo turns from 0 to 180 degree        
#         set_angle(channel, i)
#         time.sleep(0.01)                                           
#     time.sleep(0.5)
#     for i in range(180): # The servo turns from 180 to 0 degree        
#         set_angle(channel, 180-i)
#         time.sleep(0.01)
#     time.sleep(0.5)



# if __name__ == "__main__":
#     channel = 2
#     while True:
#         test(channel)

import time
from adafruit_motor import servo

class ServoMotors:
    def __init__ (self, pca, channel, min_pulse, max_pulse, actuation_range):
        self.pca = pca 
        self.channel = channel
        self.servo = servo.Servo(pca.channels[channel], min_pulse = min_pulse, max_pulse = max_pulse, actuation_range = actuation_range)
    def set_angle(self, angle):
        self.servo.angle = angle
    def test(self):
        for i in range(180):        
            self.set_angle(i)
            time.sleep(0.01)    
        time.sleep(0.5)
        for i in range(180):    
            self.set_angle(180 - i)
            time.sleep(0.01)
        time.sleep(0.5)
    def run_test(self):
        while True:
            self.test()
    def stop(self):
        self.set_angle(90)  
    

if __name__ == "__main__":
    from board import SCL, SDA
    import busio
    from adafruit_pca9685 import PCA9685

    i2c = busio.I2C(SCL, SDA)
    pca = PCA9685(i2c, address=0x5f) 
    pca.frequency = 50
    servo_motor = ServoMotors(pca, channel=1, min_pulse= 500, max_pulse = 2400, actuation_range=180)
    servo_motor.run_test()
    servo_motor.stop()