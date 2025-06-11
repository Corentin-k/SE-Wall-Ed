from gpiozero import DistanceSensor
from time import sleep

class UltrasonicSensor:
    def __init__(self, trigger_pin=23, echo_pin=24, max_distance=2):
        self.sensor = DistanceSensor(trigger=trigger_pin, echo=echo_pin, max_distance=max_distance)

    def get_distance_cm(self):
        return round(self.sensor.distance * 100, 2)

    def print_distance(self):
        distance = self.get_distance_cm()
        print(f"{distance:.2f} cm")


# Exemple d'utilisation
if __name__ == "__main__":
    ultrasonic = UltrasonicSensor()
    try:
        while True:
            ultrasonic.print_distance()
            sleep(0.05)
    except KeyboardInterrupt:
        print("Arrêt du capteur ultrason.")
