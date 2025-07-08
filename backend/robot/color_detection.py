import cv2
import numpy as np
import time
from robot.controller import Controller
from sensors.rgb_leds import RGBLEDs
from robot.config import Left_R, Left_G, Left_B, Right_R, Right_G, Right_B

# ============ COULEURS FIXES À DÉTECTER ============
# Seules les couleurs Rouge et Vert, avec des plages plus restrictives pour limiter les faux positifs
color_ranges = {
    'Rouge': ([0, 180, 120], [8, 255, 255], (0, 0, 255)),   # resserré sur le rouge vif
    'Vert': ([45, 120, 80], [85, 255, 255], (0, 255, 0)),   # resserré sur le vert franc
}

class ColorDetectionController(Controller):
    """
    Contrôleur pour la détection de couleur du robot.
    Gère la détection et l'annotation des couleurs dans le flux vidéo.
    """
    
    # Couleurs à détecter (seulement Rouge et Vert)
    COLOR_RANGES = {
        'Rouge': ([0, 180, 120], [8, 255, 255], (0, 0, 255)),
        'Vert': ([45, 120, 80], [85, 255, 255], (0, 255, 0)),
    }
    
    def __init__(self, robot):
        super().__init__(robot)
        self.enabled = True
        self.detected_colors = []
        self.robot = robot
        self.detection_threshold = 1200  # seuil augmenté pour limiter les petits faux positifs
       
        
    def start(self):
        """Initialise le contrôleur de détection de couleur"""
        self.enabled = True
        
    def update(self):
        """Mise à jour continue de la détection (appelée par le thread du contrôleur)"""
        if self.enabled:
            # La détection se fait automatiquement via get_camera_frame_with_colors
            pass
    
    def detect_and_draw_colors(self, frame):
        """
        Détecte et dessine les couleurs sur l'image
        :param frame: Image OpenCV (format BGR)
        :return: Liste des couleurs détectées
        """
        if not self.enabled:
            return []
            
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color_to_hex = {
            "Rouge": "#FF0000",
            "Vert": "#00FF00",
        }
        detected_colors = []
        color_found = None

        for name, (lower, upper, bgr_color) in self.COLOR_RANGES.items():
            lower_np = np.array(lower)
            upper_np = np.array(upper)
            mask = cv2.inRange(hsv, lower_np, upper_np)
        
            # Filtrage morphologique plus fort pour réduire le bruit
            kernel = np.ones((7, 7), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            
            # Trouver les contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                if cv2.contourArea(cnt) > self.detection_threshold:
                    x, y, w, h = cv2.boundingRect(cnt)
                    # Dessiner le rectangle
                    cv2.rectangle(frame, (x, y), (x + w, y + h), bgr_color, 2)
                    # Ajouter le texte
                    cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, bgr_color, 2)
                    detected_colors.append({
                        'name': name,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2
                    })
                    color_found = name
                    break  # Une seule détection par couleur

        # Allumer les LEDs selon la couleur détectée (priorité à la première trouvée)
        if color_found and color_found in color_to_hex:
            if detected_colors[0]['name'] == 'Rouge':
                try:
                    self.robot.ws2812.set_all_led_color(255, 0, 0)  # Utiliser set_all_led_color
                    self.robot.leds.set_color_hex(color_to_hex[color_found])
                except Exception as e:
                    print(f"Erreur LEDs Rouge: {e}")
            elif detected_colors[0]['name'] == 'Vert':
                try:
                    self.robot.ws2812.set_all_led_color(0, 255, 0)  # Utiliser set_all_led_color
                    self.robot.leds.set_color_hex(color_to_hex[color_found])
                except Exception as e:
                    print(f"Erreur LEDs Vert: {e}")
        else:
            try:
                self.robot.ws2812.set_all_led_color(0, 0, 0)  # Utiliser set_all_led_color
                self.robot.leds.set_color_hex("#000000")
            except Exception as e:
                print(f"Erreur extinction LEDs: {e}")  

        self.detected_colors = detected_colors
        return detected_colors

    def on_stop(self):
        """
        Appelée lors de l'arrêt par le contrôleur
        """
        self.enabled = False
        self.robot.leds.clear_all()

    def get_camera_frame_with_colors(self):
        """
        Récupère une frame de la caméra avec détection de couleur
        :return: Frame JPEG encodée avec annotations de couleur
        """
        try:
            # Récupérer la frame JPEG de la caméra
            frame_bytes = self.robot.camera.get_frame()
            if frame_bytes is None:
                return None

            # Décoder l'image JPEG en format OpenCV
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                return frame_bytes  # Retourner la frame originale si décodage échoue

            # PAS d'inversion horizontale - caméra dans son orientation naturelle

            # Appliquer la détection de couleur
            detected_colors = self.detect_and_draw_colors(frame)
            
            # Log des détections
            if detected_colors:
                color_names = [color['name'] for color in detected_colors]
                print(f"Couleurs détectées: {color_names}")

            # Ré-encoder l'image en JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes()

        except Exception as e:
            # En cas d'erreur, retourner la frame originale
            return self.robot.camera.get_frame()
    
    def enable_detection(self, enabled=True):
        """
        Active ou désactive la détection de couleur
        :param enabled: True pour activer, False pour désactiver
        """
        self.enabled = enabled
        print(f"Détection de couleur {'activée' if enabled else 'désactivée'}")
    
    def get_detected_colors(self):
        """
        Retourne la liste des couleurs actuellement détectées
        :return: Liste des couleurs avec leurs positions
        """
        return self.detected_colors.copy()
    
    def set_detection_threshold(self, threshold):
        """
        Modifie le seuil de détection (taille minimum des objets)
        :param threshold: Nouveau seuil en pixels
        """
        self.detection_threshold = threshold

# La fonction main et la version utilitaire sont laissées pour test manuel si besoin
def detect_and_draw_colors(frame, color_ranges):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    detected_colors = []

    for name, (lower, upper, bgr_color) in color_ranges.items():
        lower_np = np.array(lower)
        upper_np = np.array(upper)
        mask = cv2.inRange(hsv, lower_np, upper_np)
        kernel = np.ones((7, 7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if cv2.contourArea(cnt) > 1200:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), bgr_color, 2)
                cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, bgr_color, 2)
                detected_colors.append(name)
                break  # on s'arrête dès qu'on en détecte une de cette couleur

    return detected_colors

def main():
    cam = None
    try:
        while True:
            frame_bytes = cam.get_frame()
            if frame_bytes is None:
                print("Erreur : image non capturée.")
                time.sleep(0.1)
                continue

            # Décodage JPEG en image OpenCV
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                print("Erreur : décodage image.")
                continue

            frame = cv2.flip(frame, 1)
            detected_colors = detect_and_draw_colors(frame, color_ranges)

            if detected_colors:
                print("Couleurs détectées :", detected_colors)

            # Affichage de l'image avec les annotations
            cv2.imshow("Détection couleurs - Caméra", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Arrêt par l'utilisateur.")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
