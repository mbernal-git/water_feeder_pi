"""
File: UltrasonicSensorModule
Author: 
Description: Measure distance from top of the reservoir to the water surface. 
Using mode 1
References: https://wiki.dfrobot.com/Weatherproof_Ultrasonic_Sensor_With_Separate_Probe_SKU_SEN0208
"""
import serial

class UltrasonicSensorModule:
    def __init__(self):
        self.ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)

    def get_distance(self):
        if self.ser.in_waiting >= 4:
            raw_data = self.ser.read(4)
            print(f"Raw data receved: {raw_data}")
            try:
                buffer_rtt = self.ser.read(10)
                print(f"{buffer_rtt}")
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                return None
            
            print(f"Received buffer: {buffer_rtt}")

            if buffer_rtt[0] == 0xFF:
                checksum = (buffer_rtt[0] + buffer_rtt[1] + buffer_rtt[2]) & 0xFF
                if buffer_rtt[3] == checksum:
                    distance = (buffer_rtt[1] << 8) + buffer_rtt[2]
                    return distance
            else:
                print("Invalid data received")
        else:
            print("No data waiting in serial buffer")
        return None
