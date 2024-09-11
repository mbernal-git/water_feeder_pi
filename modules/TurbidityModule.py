"""
File: TurbidityModule
Author: Hanxun
Description:
"""
import RPi.GPIO as GPIO

class TurbidityModule:
    def __init__(self, id, sensor_pin):
        self.id = id
        self.sensor_pin = sensor_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sensor_pin, GPIO.IN)

    def read_turbidity(self):
        analog_value = GPIO.input(self.sensor_pin)
        voltage = analog_value * 3.3 / 255
        turbidity = (voltage - 0.4) / 0.01
        return turbidity

    def cleanup(self):
        GPIO.cleanup()
