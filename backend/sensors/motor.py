import logging
import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor
import asyncio

MOTOR_M1_IN1 =  15      #Define the positive pole of M1
MOTOR_M1_IN2 =  14      #Define the negative pole of M1
MOTOR_M2_IN1 =  12      #Define the positive pole of M2
MOTOR_M2_IN2 =  13      #Define the negative pole of M2
MOTOR_M3_IN1 =  11      #Define the positive pole of M3
MOTOR_M3_IN2 =  10      #Define the negative pole of M3
MOTOR_M4_IN1 =  8       #Define the positive pole of M4
MOTOR_M4_IN2 =  9       #Define the negative pole of M4

logger = logging.getLogger(__name__)

def map_range(x,in_min,in_max,out_min,out_max):
  return (x - in_min)/(in_max - in_min) *(out_max - out_min) +out_min


class Motors:
    def __init__(self):
        i2c = busio.I2C(SCL, SDA)
        # Create a simple PCA9685 class instance.
        #  pwm_motor.channels[7].duty_cycle = 0xFFFF
        pwm_motor = PCA9685(i2c, address=0x5f) #default 0x40
        pwm_motor.frequency = 50

        self.motor1 = motor.DCMotor(pwm_motor.channels[MOTOR_M1_IN1],pwm_motor.channels[MOTOR_M1_IN2] )
        self.motor1.decay_mode = (motor.SLOW_DECAY)
        self.motor1.throttle = 0
        self.motor2 = motor.DCMotor(pwm_motor.channels[MOTOR_M2_IN1],pwm_motor.channels[MOTOR_M2_IN2] )
        self.motor2.decay_mode = (motor.SLOW_DECAY)
        self.motor2.throttle = 0
        self.motor3 = motor.DCMotor(pwm_motor.channels[MOTOR_M3_IN1],pwm_motor.channels[MOTOR_M3_IN2] )
        self.motor3.decay_mode = (motor.SLOW_DECAY)
        self.motor3.throttle = 0
        self.motor4 = motor.DCMotor(pwm_motor.channels[MOTOR_M4_IN1],pwm_motor.channels[MOTOR_M4_IN2] )
        self.motor4.decay_mode = (motor.SLOW_DECAY)
        self.motor4.throttle = 0

        self.smooth_motor_task = None

    def set_motor_speed(self, channel, motor_speed, forward = True):
        if motor_speed > 100:
            motor_speed = 100
        elif motor_speed < 0:
            motor_speed = 0
        speed = map_range(motor_speed, 0, 100, 0, 1.0)
        if not forward:
            speed = -speed

        if channel == 1:
            self.motor1.throttle = speed
        elif channel == 2:
            self.motor2.throttle = speed
        elif channel == 3:
            self.motor3.throttle = speed
        elif channel == 4:
            self.motor4.throttle = speed
            
    def coast_motor(self, channel):
        if channel == 1:
            self.motor1.decay_mode = (motor.FAST_DECAY)
        elif channel == 2:
            self.motor2.decay_mode = (motor.FAST_DECAY)
        elif channel == 3:
            self.motor3.decay_mode = (motor.FAST_DECAY)
        elif channel == 4:
            self.motor4.decay_mode = (motor.FAST_DECAY)

    def uncoast_motor(self, channel):
        if channel == 1:
            self.motor1.decay_mode = (motor.SLOW_DECAY)
        elif channel == 2:
            self.motor2.decay_mode = (motor.SLOW_DECAY)
        elif channel == 3:
            self.motor3.decay_mode = (motor.SLOW_DECAY)
        elif channel == 4:
            self.motor4.decay_mode = (motor.SLOW_DECAY)
    def uncoast(self):
        self.uncoast_motor(1)

    def coast(self):
        self.coast_motor(1)
        
    def set_speed(self, speed: int, forward = True):
        self.set_motor_speed(1, speed, forward)

    smooth_step_count = 20 # how many time do we actualise the speed during acceleration

    async def __smooth_speed__(self, target_speed, forward = True, acceleration_rate = 1):
        while True:
            current_speed = map_range(self.motor1.throttle, -1, 1, -100, 100)
            speed_diff = target_speed - current_speed
            max_diff = acceleration_rate / self.smooth_step_count
            if speed_diff > 0 :
                speed_diff = min(max_diff, speed_diff)
            else:
                speed_diff = max(-max_diff, speed_diff)

            next_target_speed = current_speed + speed_diff
            if abs(next_target_speed) > abs(target_speed):
                next_target_speed = target_speed

            self.set_speed(abs(next_target_speed), next_target_speed > 0)
            if target_speed == current_speed:
                break
            asyncio.sleep(1 / self.smooth_step_count)


    def smooth_speed(self, target_speed, forward = True):
        if(self.smooth_motor_task != None):
            self.smooth_motor_task.cancel()
        self.smooth_motor_task = asyncio.create_task(self.__smooth_speed__(target_speed))
        return self.smooth_motor_task



async def main():
    motors = Motors()
    try:
        for i in range(10, 25):
            print("testing speed : ", i * 10)
            await motors.smooth_speed(100, True, i * 10)
            await asyncio.sleep(0.1)
            await motors.smooth_speed(-100, True, i * 10)
            await asyncio.sleep(0.1)
        await motors.smooth_speed(0)
    except asyncio.CancelledError:
        motors.set_speed(0)

if __name__ == "__main__":
    asyncio.run(main())
