"""
File: PumpModule
Author:
Description: Toggle water pump
"""
import RPi.GPIO as GPIO
from time import sleep

class PumpModule:
  def __init__(self, pin):
    self.pin = pin
    self.pins_set = False
    # Set GPIO interface
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
    self.pins_set = True

    # Pump initially turned off
    self.stop()

  def start(self):
    GPIO.output(self.pin, GPIO.HIGH)
    print("Pump started")
    

  def stop(self):
    GPIO.output(self.pin, GPIO.LOW)
    print("Pump stopped")


  def get_status(self):
    return GPIO.input(self.pin)
  
  def monitor_status(self):
    try:
      while True:
        pump_status = self.get_status()
        print(f"Pump status: {'ON' if pump_status else 'OFF'}")
        sleep(5)
    except KeyboardInterrupt:
      print("Force stopping pump")
    finally:
      self.cleanup()

  def cleanup(self):
    GPIO.cleanup() 
    print("GPIO cleaned up")