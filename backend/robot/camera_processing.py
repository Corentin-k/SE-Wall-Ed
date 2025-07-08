import cv2 as cv
import time
import numpy as np

class Arrow:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def draw(self, frame):
        cv.arrowedLine(frame, self.start, self.end, (255, 0, 0), 2)

    def is_similar(self, other, error_threshold=10):
        assert isinstance(other, Arrow), "Other must be an instance of Arrow"

        start_distance = ((self.start[0] - other.start[0]) ** 2 + (self.start[1] - other.start[1]) ** 2) ** 0.5
        end_distance = ((self.end[0] - other.end[0]) ** 2 + (self.end[1] - other.end[1]) ** 2) ** 0.5
        return start_distance < error_threshold and end_distance < error_threshold
    
    def get_direction(self):
        return (self.end[0] - self.start[0], self.end[1] - self.start[1])

    def __str__(self):
        return f"Arrow from {self.start} to {self.end}"
    
    def __repr__(self):
        return self.__str__()

class PersistentArrowDetector:
    class ArrowDetection:
        def __init__(self, arrow):
            self.arrow = arrow
            self.hit_count = 0
            self.first_hit_time = time.time()
            self.last_hit_time = time.time()
        
        def add_new_hit(self, arrow):
            self.arrow = arrow
            self.hit_count += 1
            self.last_hit_time = time.time()
        

    def __init__(self, max_time_without_hits=0.5):
        self.detected_arrows = []
        self.max_time_without_hits = max_time_without_hits

    def push_arrow(self, arrow):
        for detection in self.detected_arrows:
            if detection.arrow.is_similar(arrow) and (time.time() - detection.last_hit_time) < self.max_time_without_hits:
                detection.add_new_hit(arrow)
                return

        new_detection = self.ArrowDetection(arrow)
        self.detected_arrows.append(new_detection)
    
    def get_max_hit_arrow(self):
        if len(self.detected_arrows) == 0:
            return None

        for detection in self.detected_arrows:
            if (time.time() - detection.last_hit_time) > self.max_time_without_hits:
                self.detected_arrows.remove(detection)
        
        max_hit_arrow_index = -1
        for i, detection in enumerate(self.detected_arrows):
            if detection:
                if max_hit_arrow_index == -1 or detection.hit_count > self.detected_arrows[max_hit_arrow_index].hit_count:
                    max_hit_arrow_index = i

        return self.detected_arrows[max_hit_arrow_index] if max_hit_arrow_index != -1 else None

persistent_arrow_detector = PersistentArrowDetector()

def find_arrows(frame):
    canny_frame = cv.Canny(frame, 255/3, 255)
    contours, _ = cv.findContours(canny_frame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv.contourArea(contour) < 100:
            continue

        precision = 0.02 * cv.arcLength(contour, True)
        sommets = cv.approxPolyDP(contour, precision, True)

        # detecting arrows

        if len(sommets) != 7:
            continue

        # find the only two lines that are perpendicular to each other
        direction_edges = None

        for i in range(len(sommets)):
            perpendicular_count = 0
            perpendicular_line_index = -1

            ax1, ay1 = sommets[i][0]
            ax2, ay2 = sommets[(i + 1) % len(sommets)][0]
            magnitude_a = ((ax2 - ax1) ** 2 + (ay2 - ay1) ** 2) ** 0.5
            vector_a = ((ax2 - ax1) / magnitude_a, (ay2 - ay1) / magnitude_a)

            for j in range(len(sommets)):
                if i == j:
                    continue

                x1, y1 = sommets[j][0]
                x2, y2 = sommets[(j + 1) % len(sommets)][0]

                magnitude_b = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                vector_b = ((x2 - x1) / magnitude_b, (y2 - y1) / magnitude_b)

                perpendicular_threshold = 0.25  # Adjust this threshold as needed
                dot_product = vector_a[0] * vector_b[0] + vector_a[1] * vector_b[1]
                # cv.putText(frame, f"Dot Product: ", (ax1, ay1), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                # cv.putText(frame, f"{round(dot_product, 2)}", (ax1 + 100 + j * 20, ay1), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                # print(f"Dot Product: {round(dot_product, 2)}")
                if abs(dot_product) < perpendicular_threshold and abs(magnitude_a - magnitude_b) < 0.1 * max(magnitude_a, magnitude_b) and magnitude_a > 30:
                    perpendicular_count += 1
                    perpendicular_line_index = j

            if perpendicular_count == 1 and ((sommets[(i + 1) % len(sommets)][0] == sommets[perpendicular_line_index][0]).all()):
                # Draw the contour and the arrow
                # cv.line(frame, tuple(sommets[i][0]), tuple(sommets[(i + 1) % len(sommets)][0]), (0, 255, 0), 2)
                # cv.line(frame, tuple(sommets[perpendicular_line_index][0]), tuple(sommets[(perpendicular_line_index + 1) % len(sommets)][0]), (0, 255, 0), 2)
                common_point = sommets[perpendicular_line_index]
                
                not_common_points = [sommets[i], sommets[(perpendicular_line_index + 1) % len(sommets)]]

                not_common_points_middle = (
                    (not_common_points[0][0][0] + not_common_points[1][0][0]) // 2,
                    (not_common_points[0][0][1] + not_common_points[1][0][1]) // 2
                )

                # cv.arrowedLine(frame, tuple(not_common_points_middle), tuple(common_point[0]), (255, 0, 0), 2)
                persistent_arrow_detector.push_arrow(Arrow(not_common_points_middle, common_point[0]))

def get_arrow_direction():
    """
    Returns the direction of the most detected arrow.
    :return: A tuple representing the direction of the arrow, or None if no arrow is detected.
    """
    detection = persistent_arrow_detector.get_max_hit_arrow()
    if detection is None:
        return None
    return "right" if detection.arrow.get_direction()[0] > 0 else "left"

def camera_processing_thread(robot):
    while True:
        frame_bytes = robot.camera.get_frame()
        if frame_bytes is None:
            return None

        # 1) Décodage du JPEG
        np_arr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv.imdecode(np_arr, cv.IMREAD_COLOR)
        
        find_arrows(frame)

        if get_arrow_direction() is not None:
            print(f"Detected arrow direction: {get_arrow_direction()}")

        time.sleep(0.1)

def start_camera_processing(robot):
    """
    Starts the camera processing thread for the robot.
    :param robot: The robot instance with a camera.
    """
    import threading
    camera_thread = threading.Thread(target=camera_processing_thread, args=(robot,))
    camera_thread.daemon = True  # Allows the thread to exit when the main program exits
    camera_thread.start()
    return camera_thread