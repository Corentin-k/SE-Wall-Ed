import logging
import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor
import threading

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

        self.acceleration_rate = 50 # default acceleration rate

        self.motor1 = motor.DCMotor(pwm_motor.channels[MOTOR_M1_IN1],pwm_motor.channels[MOTOR_M1_IN2] )
        self.motor1.decay_mode = (motor.SLOW_DECAY)
        self.motor1.throttle = 0
        self.motor1_target_speed = 0
        self.motor2 = motor.DCMotor(pwm_motor.channels[MOTOR_M2_IN1],pwm_motor.channels[MOTOR_M2_IN2] )
        self.motor2.decay_mode = (motor.SLOW_DECAY)
        self.motor2.throttle = 0
        self.motor2_target_speed = 0
        self.motor3 = motor.DCMotor(pwm_motor.channels[MOTOR_M3_IN1],pwm_motor.channels[MOTOR_M3_IN2] )
        self.motor3.decay_mode = (motor.SLOW_DECAY)
        self.motor3.throttle = 0
        self.motor3_target_speed = 0
        self.motor4 = motor.DCMotor(pwm_motor.channels[MOTOR_M4_IN1],pwm_motor.channels[MOTOR_M4_IN2] )
        self.motor4.decay_mode = (motor.SLOW_DECAY)
        self.motor4.throttle = 0
        self.motor4_target_speed = 0

        self.motor_thread = threading.Thread(target=self._smooth_speed_thread, daemon=True)
        self.motor_thread.start()

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

    def _smooth_speed_thread(self):
        while True:
            current_speed = map_range(self.motor1.throttle, -1, 1, -100, 100)
            speed_diff = self.motor1_target_speed - current_speed
            if speed_diff != 0:
                max_diff = self.acceleration_rate / self.smooth_step_count
                if speed_diff > 0 :
                    speed_diff = min(max_diff, speed_diff)
                else:
                    speed_diff = max(-max_diff, speed_diff)

                next_target_speed = current_speed + speed_diff

                self.set_speed(abs(next_target_speed), next_target_speed > 0)
            
            time.sleep(1 / self.smooth_step_count)


    def smooth_speed(self, target_speed, acceleration = 50):
        self.acceleration_rate = acceleration
        self.motor1_target_speed = target_speed
    
    def smooth_speed_and_wait(self, target_speed, acceleration = 50):
        self.smooth_speed(target_speed, acceleration)
        speed_diff = abs(self.motor1_target_speed - map_range(self.motor1.throttle, -1, 1, -100, 100))
        time.sleep(1 / self.smooth_step_count * abs(speed_diff) / 100)



def main():
    motors = Motors()
    try:
        for i in range(10, 25):
            print("testing speed : ", i * 10)
            motors.smooth_speed(100, i * 10)
            time.sleep(3)
            motors.smooth_speed(-100, i * 10)
            time.sleep(3)
        motors.smooth_speed(0)
    except KeyboardInterrupt:
        motors.set_speed(0)

if __name__ == "__main__":
    main()
