from sensors import *
from robot.config import *
import time
from robot.controller import Controller

# Import pour WebSocket (sera None si pas disponible)
try:
    from api import socketio
except ImportError:
    socketio = None

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

class RadarController(Controller):
    def __init__(self, robot):
        super().__init__(robot)
        self.result = []

    def radar_scan(self, min_angle=0, max_angle=180, step=5):
        """
        Effectue un scan radar et diffuse les résultats via WebSocket
        """
        self.result = []
        pwm0_min = min_angle
        
        # Reset position
        self.robot.pan_servo.set_angle(pwm0_min)
        time.sleep(0.2)
        
        # Scan de gauche à droite
        current_angle = pwm0_min
        angles = []
        distances = []
        
        while current_angle <= max_angle:
            self.robot.pan_servo.set_angle(current_angle)
            time.sleep(0.1)  # Attendre que le servo se positionne
            
            dist = self.robot.ultra.get_distance_cm()
            self.result.append([dist, current_angle])
            angles.append(current_angle)
            distances.append(dist)
            
            current_angle += step
        
        # Retourner au centre
        self.robot.pan_servo.set_angle(90)
        
        # Diffuser les données via WebSocket si disponible
        if socketio:
            try:
                radar_data = {
                    'angles': angles,
                    'distances': distances,
                    'min_angle': min_angle,
                    'max_angle': max_angle,
                    'timestamp': time.time()
                }
                socketio.emit('radar_scan_result', radar_data)
                print(f"Radar scan diffusé: {len(angles)} points")
            except Exception as e:
                print(f"Erreur diffusion radar: {e}")
        
        return self.result

    def start(self):
        
        self.robot.motor_servomotor.set_angle(map_range(0, -98, 82, 0, 180))
        self.robot.tilt_servo.set_angle(90)
        self.robot.pan_servo.set_angle(90)

    def update(self):
        dist = self.robot.ultra.get_distance_cm()
        seuil = 30
        vitesse = 25
        while dist < seuil:   
            self.robot.motor.smooth_speed(0)
            time.sleep(0.5)
            
            # Faire un scan radar automatique
            self.radar_scan(min_angle=30, max_angle=150, step=10)
            
            if self.result:
                dist_max = max([item[0] for item in self.result])
                angle_max = max([item[1] for item in self.result if item[0] == dist_max])
                if angle_max < 90:
                    angle_max = map_range(37, -98, 82, 0, 180)
                    self.robot.motor_servomotor.set_angle(angle_max)
                    self.robot.pan_servo.set_angle(angle_max)
                else:
                    angle_max = map_range(-37, -98, 82, 0, 180)
                    self.robot.motor_servomotor.set_angle(angle_max)
                    self.robot.pan_servo.set_angle(angle_max)
                dist = seuil + 1
                self.robot.motor.smooth_speed(vitesse)
                time.sleep(1)
        self.robot.motor.smooth_speed(vitesse)
        dist = self.robot.ultra.get_distance_cm()

    def dist_redress(robot):
            mark = 0
            distValue = robot.ultra.get_distance_cm()
            while True:
                distValue = robot.ultra.get_distance_cm()
                if distValue > 900:
                    mark += 1
                elif mark > 5 or distValue < 900:
                    break
                print(distValue)
            return round(distValue, 2)
