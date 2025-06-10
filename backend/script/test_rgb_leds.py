
from sensors.rgb_leds import RGBLEDs
import keyboard  
import time
from robot.config import Left_R, Left_G, Left_B, Right_R, Right_G, Right_B

MAPPING = {
    'r': 'L_R',
    'g': 'L_G',
    'b': 'L_B',
    'u': 'R_R',
    'v': 'R_G',
    'n': 'R_B',
}
def start_colors():
    leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
    pressed = set()

    def on_down(e):
        if e.name in MAPPING:
            pressed.add(e.name)

    def on_up(e):
        if e.name in MAPPING:
            pressed.discard(e.name)

    keyboard.on_press(on_down)
    keyboard.on_release(on_up)

    print("Maintenez r/g/b/u/v/n pour allumer, relâchez pour éteindre, q pour quitter.")
    try:
        while True:
            if keyboard.is_pressed('q'):
                break
            leds.clear_all()

            for key in pressed:
                if key in MAPPING:
                    leds.highled(MAPPING[key])  
            time.sleep(0.05)
    finally:
        leds.destroy()
        keyboard.unhook_all()

colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF, 0x6F00D2, 0xFF5809]
def color_loop():
    leds = RGBLEDs(Left_R, Left_G, Left_B, Right_R, Right_G, Right_B)
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
    leds.set_color_hex("#FF8800")
    time.sleep(2)
    leds.destroy()

if __name__ == "__main__":
    start_colors()
