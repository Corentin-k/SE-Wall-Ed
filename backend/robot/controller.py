from sensors.motor import Motor

# Instance globale du moteur
motor = Motor()

def set_motor_speed(speed):
    motor.set_speed(speed)
    return f"Speed set to {speed}"

def stop_motor():
    motor.stop()
    return "Motor stopped"
