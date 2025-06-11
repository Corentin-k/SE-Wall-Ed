import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sensors.line_tracking import LineTracker


if __name__ == "__main__":
    tracker = LineTracker()
    try:
        while True:
            tracker.trackLineProcessing()
    except KeyboardInterrupt:
        print("Arrêt du robot.")