from sensors import Camera
import cv2
import numpy as np
import time

# ============ COULEURS FIXES À DÉTECTER ============
color_ranges = {
    'Rouge': ([0, 150, 120], [5, 255, 255]),
    'Vert': ([35, 80, 60], [90, 255, 255]),
    'Bleu': ([105, 120, 50], [130, 255, 255]),
    'Jaune': ([18, 100, 100], [35, 255, 255]),
}

def detect_colors(frame, color_ranges):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    detected_colors = []
    for name, (lower, upper) in color_ranges.items():
        lower_np = np.array(lower)
        upper_np = np.array(upper)
        mask = cv2.inRange(hsv, lower_np, upper_np)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt) > 500:
                detected_colors.append(name)
                break
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
            detected_colors = detect_colors(frame, color_ranges)
            if detected_colors:
                print(detected_colors)
            # Pour afficher l'image avec OpenCV (optionnel)
            # cv2.imshow("Camera", frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
    except KeyboardInterrupt:
        print("Arrêt par l'utilisateur.")
    finally:
        Camera.shutdown()
        # cv2.destroyAllWindows()

if __name__ == "__main__":
    main()