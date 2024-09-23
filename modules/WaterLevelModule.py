# File: WaterLevelModule
# Author: 
# Description:
# References: https://wiki.dfrobot.com/Non_Contact_Capacitive_Liquid_Level_Sensor_SKU_SEN0368

import RPi.GPIO as GPIO
import time

class WaterLevelModule:
  def __init__(self, in_pin, mode_pin, sensor_location):
    # Set GPIO interface
    GPIO.setmode(GPIO.BCM)

    # IO1 Liquid Sensor Forward/backward Output Select (Right, Blue)
    self.mode_pin = mode_pin

    # IO2 Liquid Level Signal Output (Right, Green)
    self.in_pin = in_pin

    self.sensor_location = sensor_location

    self.pins_set = False

    GPIO.setup(self.mode_pin, GPIO.OUT)

    # Set the pull_up_down to down as per jumper cap
    # down is set to read absence of water
    GPIO.setup(self.in_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.output(self.mode_pin, True) 

  def is_low(self):
    return GPIO.input(self.in_pin) == 0

  def get_water_level(self):
    if self.sensor_location == 'reservoir':
      if not self.is_low():
        return "low"
      else:
        return "good"
    elif self.sensor_location == "waste":
      if self.is_low():
        return "Waste water tank can accept more water."
      else:
        return "Waste water tank is full! Please empty."

  def monitor_water_level(self):
    try:
      while True:
        water_level_status = self.get_water_level()
        print(water_level_status)
        time.sleep(2)
    except KeyboardInterrupt:
      print("Monitoring stopped.")
    finally:
      self.cleanup()

  def cleanup(self):
    if self.pins_set:
      GPIO.cleanup(self.in_pin)
      GPIO.cleanup(self.mode_pin)
      GPIO.cleanup()
      self.pins_set = False
