import RPi.GPIO as GPIO
from gpiozero import PWMOutputDevice as PWM
import time

colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF, 0x6F00D2, 0xFF5809]

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class RGBLEDs:
    def __init__(self, left_r, left_g, left_b, right_r, right_g, right_b):
        self.Left_R = left_r
        self.Left_G = left_g
        self.Left_B = left_b
        self.Right_R = right_r
        self.Right_G = right_g
        self.Right_B = right_b
        self.L_R = None
        self.L_G = None
        self.L_B = None
        self.R_R = None
        self.R_G = None
        self.R_B = None

    def setup(self):
        self.L_R = PWM(pin=self.Left_R, initial_value=1.0, frequency=2000)
        self.L_G = PWM(pin=self.Left_G, initial_value=1.0, frequency=2000)
        self.L_B = PWM(pin=self.Left_B, initial_value=1.0, frequency=2000)
        self.R_R = PWM(pin=self.Right_R, initial_value=1.0, frequency=2000)
        self.R_G = PWM(pin=self.Right_G, initial_value=1.0, frequency=2000)
        self.R_B = PWM(pin=self.Right_B, initial_value=1.0, frequency=2000)
    
    def highled(self, led,value):
        value = map_value(value, 0, 255, 0, 1.00)
        if led == 'L_R':
            self.L_R.value = value
        elif led == 'L_G':
            self.L_G.value = value
        elif led == 'L_B':
            self.L_B.value = value
        elif led == 'R_R':
            self.R_R.value = value
        elif led == 'R_G':
            self.R_G.value = value
        elif led == 'R_B':
            self.R_B.value = value

    def setAllColor(self, col):
        """col: int, couleur hex ex: 0x112233"""
        R_val = (col & 0xff0000) >> 16
        G_val = (col & 0x00ff00) >> 8
        B_val = (col & 0x0000ff)
        R_val = map_value(R_val, 0, 255, 0, 1.00)
        G_val = map_value(G_val, 0, 255, 0, 1.00)
        B_val = map_value(B_val, 0, 255, 0, 1.00)
        self.L_R.value = 1.0 - R_val
        self.L_G.value = 1.0 - G_val
        self.L_B.value = 1.0 - B_val
        self.R_R.value = 1.0 - R_val
        self.R_G.value = 1.0 - G_val
        self.R_B.value = 1.0 - B_val

    def setAllRGBColor(self, R, G, B):
        R_val = map_value(R, 0, 255, 0, 1.00)
        G_val = map_value(G, 0, 255, 0, 1.00)
        B_val = map_value(B, 0, 255, 0, 1.00)
        self.L_R.value = 1.0 - R_val
        self.L_G.value = 1.0 - G_val
        self.L_B.value = 1.0 - B_val
        self.R_R.value = 1.0 - R_val
        self.R_G.value = 1.0 - G_val
        self.R_B.value = 1.0 - B_val

    def loop(self):
        while True:
            for col in colors:
                self.setAllColor(col)
                time.sleep(0.5)

    def destroy(self):
        self.L_R.close()
        self.L_G.close()
        self.L_B.close()
        self.R_R.close()
        self.R_G.close()
        self.R_B.close()

if __name__ == "__main__":
    leds = RGBLEDs(17, 27, 22, 10, 9, 11) 
    leds.setup()
    try:
        leds.loop()
    except KeyboardInterrupt:
        leds.destroy()