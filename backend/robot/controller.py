class Controller:
    def __init__(self, robot):
        self.robot = robot

    
    def start(self):
        raise RuntimeError("This method should be overridden in a subclass.")

    def update(self):
        raise RuntimeError("This method should be overridden in a subclass.")
    
    def stop(self):
        raise RuntimeError("This method should be overridden in a subclass.")