import time
import board
import busio
from adafruit_bus_device.i2c_device import I2CDevice
from buzzer import Buzzer

class BatteryMonitor:
    def __init__(self, i2c_address=0x48, vref=8.4, warning_threshold=6.75, r15=3000, r17=1000, adc_channel=0):
        self.vref = vref
        self.warning_threshold = warning_threshold
        self.division_ratio = r17 / (r15 + r17)
        self.adc_channel = adc_channel
        self.cmd = 0x84

        # Setup I2C
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.device = I2CDevice(self.i2c, i2c_address)

        # Prepare control byte
        self.control_byte = self.cmd | (((self.adc_channel << 2 | self.adc_channel >> 1) & 0x07) << 4)

        self.buzzer = Buzzer()

    def read_adc_value(self):
        buffer = bytearray(1)
        self.device.write_then_readinto(bytes([self.control_byte]), buffer)
        return buffer[0]

    def calculate_voltage(self, adc_value):
        return (adc_value / 255.0) * 5.0

    def get_battery_status(self):
        adc_value = self.read_adc_value()
        a0_voltage = self.calculate_voltage(adc_value)
        actual_voltage = a0_voltage / self.division_ratio
        battery_percentage = ((actual_voltage - self.warning_threshold) /
                              (self.vref - self.warning_threshold)) * 100
        return actual_voltage, battery_percentage

    def check_battery(self):
        voltage, percentage = self.get_battery_status()
        print(f"Current battery level: {percentage:.2f} %")
        if percentage < 20:
            print("Warning! The battery level is too low. Please charge in time!")
            self.buzzer.play_tune(ALERTE)


    def run(self, delay=0.5):
        while True:
            self.check_battery()
            time.sleep(delay)

ALERTE = [["E5", 3]]    

if __name__ == "__main__":
    monitor = BatteryMonitor()
    monitor.run()
