from sensors import Camera
import cv2
import numpy as np
import time

# ============ COULEURS FIXES À DÉTECTER ============
color_ranges = {
    'Rouge': ([0, 150, 120], [5, 255, 255], (0, 0, 255)),
    'Vert': ([35, 80, 60], [90, 255, 255], (0, 255, 0)),
    'Bleu': ([105, 120, 50], [130, 255, 255], (255, 0, 0)),
    'Jaune': ([18, 100, 100], [35, 255, 255], (0, 255, 255)),
}

def detect_and_draw_colors(frame, color_ranges):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    detected_colors = []

    for name, (lower, upper, bgr_color) in color_ranges.items():
        lower_np = np.array(lower)
        upper_np = np.array(upper)
        mask = cv2.inRange(hsv, lower_np, upper_np)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if cv2.contourArea(cnt) > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), bgr_color, 2)
                cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, bgr_color, 2)
                detected_colors.append(name)
                break  # on s'arrête dès qu'on en détecte une de cette couleur

    return detected_colors

def main():
    cam = Camera()
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
        Camera.shutdown()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
