import RPi.GPIO as GPIO
import threading
from gpiozero import PWMOutputDevice as PWM
import curses
import time
from robot.config import Left_R, Left_G, Left_B, Right_R, Right_G, Right_B

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def hex_to_rgb(hex_value: str) -> tuple[int, int, int]:
    hex_value = hex_value.lstrip('#')
    if len(hex_value) == 3:
        hex_value = ''.join(c * 2 for c in hex_value)
    r = int(hex_value[0:2], 16)
    g = int(hex_value[2:4], 16)
    b = int(hex_value[4:6], 16)
    return (r, g, b)

class RGBLEDs:
    def __init__(self, left_r, left_g, left_b, right_r, right_g, right_b):
        self.Left_R = left_r
        self.Left_G = left_g
        self.Left_B = left_b
        self.Right_R = right_r
        self.Right_G = right_g
        self.Right_B = right_b

    def setup(self):
        self.L_R = PWM(pin=self.Left_R, initial_value=1.0, frequency=2000)
        self.L_G = PWM(pin=self.Left_G, initial_value=1.0, frequency=2000)
        self.L_B = PWM(pin=self.Left_B, initial_value=1.0, frequency=2000)
        self.R_R = PWM(pin=self.Right_R, initial_value=1.0, frequency=2000)
        self.R_G = PWM(pin=self.Right_G, initial_value=1.0, frequency=2000)
        self.R_B = PWM(pin=self.Right_B, initial_value=1.0, frequency=2000)

    def highled(self, leds):
        if not leds:
            return
        for led in leds:
            if led == 'L_R': self.L_R.value = 0
            elif led == 'L_G': self.L_G.value = 0
            elif led == 'L_B': self.L_B.value = 0
            elif led == 'R_R': self.R_R.value = 0
            elif led == 'R_G': self.R_G.value = 0
            elif led == 'R_B': self.R_B.value = 0

    def setAllColor(self, col):
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

    def set_color_hex(self, hex_value: str):
        r, g, b = hex_to_rgb(hex_value)
        self.setAllRGBColor(r, g, b)

    def clear_all(self):
        self.L_R.value = 1.0
        self.L_G.value = 1.0
        self.L_B.value = 1.0
        self.R_R.value = 1.0
        self.R_G.value = 1.0
        self.R_B.value = 1.0

    def shutdown(self):
        self.L_R.close()
        self.L_G.close()
        self.L_B.close()
        self.R_R.close()
        self.R_G.close()
        self.R_B.close()
    
    def start_police(self, interval: float = 0.5):
        """
        Lance un clignotement rouge/bleu en arrière-plan.
        """
        # Si un police déjà en cours, on ne relance pas
        if getattr(self, "_police_thread", None) and self._police_thread.is_alive():
            return

        # Flag d’arrêt
        self._police_stop = threading.Event()

        def _police_loop():
            while not self._police_stop.is_set():
                self.set_color_hex("#FF0000")  # rouge
                time.sleep(interval)
                self.set_color_hex("#0000FF")  # bleu
                time.sleep(interval)
            # À la fin, on éteint toutes les LEDs
            self.clear_all()

        # On démarre le thread daemon
        self._police_thread = threading.Thread(target=_police_loop, daemon=True)
        self._police_thread.start()

    def stop_police(self):
        """
        Arrête le clignotement police et éteint les LEDs.
        """
        if getattr(self, "_police_stop", None):
            self._police_stop.set()
            # On peut attendre la fin si besoin :
            self._police_thread.join()
        self.clear_all()

 


MAPPING = {
    ord('r'): 'L_R',
    ord('g'): 'L_G',
    ord('b'): 'L_B',
    ord('u'): 'R_R',
    ord('v'): 'R_G',
    ord('n'): 'R_B',
}

colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF, 0x6F00D2, 0xFF5809]

def start_colors():
    leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
    leds.setup()

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(True)

    try:
        stdscr.addstr(0, 0, "Appuyez sur r/g/b/u/v/n pour allumer une ou plusieurs LEDs, q pour quitter.")
        stdscr.refresh()

        pressed = set()

        while True:
            ch = stdscr.getch()
            if ch != curses.ERR:
                if ch == ord('q'):
                    break
                elif ch in MAPPING:
                    pressed.add(ch)
            else:
                time.sleep(0.01)

            leds.clear_all()
            leds.highled([MAPPING[c] for c in pressed])

    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        leds.destroy()

def color_loop():
    leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
    leds.setup()
    try:
        while True:
            for col in colors:
                leds.setAllColor(col)
                time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        leds.destroy()

def test_hex_colors():
    leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
    leds.setup()
    leds.set_color_hex("#FF8800")
    time.sleep(2)
    leds.destroy()

if __name__ == "__main__":
    start_colors()
