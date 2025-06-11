from sensors.line_tracking import LineTracker


if __name__ == "__main__":
    tracker = LineTracker()
    try:
        while True:
            tracker.track_line_processing()
    except KeyboardInterrupt:
        print("Arrêt du robot.")