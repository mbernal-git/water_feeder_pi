"""
File: UltrasonicSensorModule.py
Author: 
Description: Measure reservoir water level by sending audio signal from top of the reservoir to water surface.
Result: JSN SRO4T 2.0 and HC-SR04 minimum measurement is 200mm which is not ideal for our design.
Action: Team decided to use 2 capactive level sensor.
Status: Abanadoned
References: https://leanpub.com/rpcultra/read#ultrasonic
"""
import RPi.GPIO as GPIO
import time

class UltrasonicSensorModule:
    def __init__(self, trig_pin, echo_pin, speed_of_sound=34300):
        # The speed of sound in cm/s (default is for room temperature: 34300 cm/s)
        # Calibration factor is speed_of_sound / 2 for round-trip distance measurement
        self.calibration_factor = speed_of_sound / 2
        self.TRIG = trig_pin
        self.ECHO = echo_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)

    def get_distance(self):
        # Ensure the trigger pin is low
        GPIO.output(self.TRIG, False)
        time.sleep(0.02)  # 20 milliseconds delay for better accuracy

        # Trigger the sensor
        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)  # Send 10µs pulse
        GPIO.output(self.TRIG, False)

        # Wait for echo start and end
        while GPIO.input(self.ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(self.ECHO) == 1:
            pulse_end = time.time()

        # Calculate pulse duration
        pulse_duration = pulse_end - pulse_start

        # Calculate distance in mm
        distance_mm = pulse_duration * self.calibration_factor * 10  # cm to mm
        distance_mm = round(distance_mm, 2)

        print(f"DEBUG: Pulse duration = {pulse_duration:.6f} seconds")
        print(f"DEBUG: Calculated distance = {distance_mm} mm")

        # Check if the distance is within an acceptable range (adjusted for short ranges)
        if 30 <= distance_mm <= 260:  # Your target range
            return distance_mm
        else:
            return "Out of Range"

# Usage example
if __name__ == "__main__":
    # Use 34300 cm/s for speed of sound at room temperature
    sensor = UltrasonicSensorModule(trig_pin=15, echo_pin=14, speed_of_sound=34300)
    
    while True:
        distance = sensor.get_distance()
        print(f"Distance: {distance} mm")
        time.sleep(0.02)  # Ensure a 20-millisecond delay between readings for accuracy
