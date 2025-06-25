from gpiozero import TonalBuzzer
from time import sleep

class Buzzer:
    def __init__(self, pin=18):
        self.buzzer = TonalBuzzer(pin)

    def play_tune(self, tune=None, mode="default" ):
        if mode == "Police":
            tune = Police
        for note, duration in tune:
            print(note if note else "Pause")
            self.buzzer.play(note)
            sleep(float(duration))
        self.buzzer.stop()

    def stop(self):
        if self.buzzer:
            try:
                self.buzzer.stop()
            except Exception:
                pass

    def shutdown(self):
        self.stop()
        if self.buzzer:
            try:
                self.buzzer.close()
            finally:
                self.buzzer = None


# Définition de la mélodie
SONG = [
    ["E5", 0.3], ["Eb5", 0.3], ["E5", 0.3], ["Eb5", 0.3],
    ["E5", 0.3], ["B4", 0.3], ["D5", 0.3], ["C5", 0.3],
    ["A4", 0.6], [None, 0.1], ["C4", 0.3], ["E4", 0.3], ["A4", 0.3],
    ["B4", 0.6], [None, 0.1], ["E4", 0.3], ["Ab4", 0.3], ["B4", 0.3],
    ["C5", 0.6], [None, 0.1], ["E4", 0.3], ["E5", 0.3], ["Eb5", 0.3],
    ["E5", 0.3], ["Eb5", 0.3], ["E5", 0.3], ["B4", 0.3], ["D5", 0.3], ["C5", 0.3],
    ["A4", 0.6], [None, 0.1], ["C4", 0.3], ["E4", 0.3], ["A4", 0.3],
    ["B4", 0.6], [None, 0.1], ["E4", 0.3], ["C5", 0.3], ["B4", 0.3], ["A4", 0.1]
]


Police = [
    ["A4", 0.5], ["E4", 0.5],
    ["A4", 0.5], ["E4", 0.5],
    ["A4", 0.5], ["E4", 0.5],
    ["A4", 0.5], ["E4", 0.5],
    ["A4", 0.5], ["E4", 0.5],
    ["A4", 0.5], ["E4", 0.5],
    ["A4", 0.5], ["E4", 0.5],
    ["A4", 0.5], ["E4", 0.5],
    ["A4", 0.5], ["E4", 0.5],
    [None, 0.2]
]
# Exemple d'utilisation
if __name__ == "__main__":
    buzzer = Buzzer()
    try:
        buzzer.play_tune(Police)
    except KeyboardInterrupt:
        buzzer.stop()
        print("Arrêt du buzzer.")
