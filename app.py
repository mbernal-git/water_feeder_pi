import os
from time import sleep, time
import threading
from modules import WaterLevelModule, TurbidityModule, mqttModule, ValveModule, RFIDModule, readWeight, PumpModule
from modules import wificonn, httpModule

class WaterFeeder:
    def __init__(self, waste_water_level_sensor_arg, turbidity_sensor, reservoir_valve, rfid_module,mqtt_client, wifi_conn, httpmodule, readWeight, pump_arg, bowl_valve_arg):
        self.waste_water_level_sensor = waste_water_level_sensor_arg
        self.turbidity_sensor = turbidity_sensor
        self.reservoir_valve = reservoir_valve
        self.rfid_module = rfid_module
        self.mqtt_client = mqtt_client
        self.wifi_conn = wifi_conn
        self.httpmodule = httpmodule
        self.readWeight = readWeight
        self.monitoring = True
        self.pump = pump_arg
        self.bowl_valve = bowl_valve_arg

        self.get_sensor_data()

        self.mqtt_client.client.subscribe("remotecommand")
        self.mqtt_client.client.on_message = self.on_message

    def get_sensor_data(self):
        waste_water_level = self.waste_water_level_sensor.is_low()
        turbidity_value = self.turbidity_sensor.read_turbidity()
        weight_value = self.readWeight.read_weight()
        waste_tank_sensor_location = self.waste_water_level_sensor.sensor_location
        ntu_id = self.turbidity_sensor.id
        # Console logs
        print(f"Waste water level: {self.waste_water_level_sensor.get_water_level()}")
        print(f"Turbidity Level: {turbidity_value}")
        print(f"waste water level: {waste_water_level}")

        # Website events
        self.httpmodule.uploadSensorData(f"{waste_tank_sensor_location}", str(waste_water_level)) # Waste Water Level
        self.httpmodule.uploadSensorData(ntu_id,turbidity_value) # Turbidity
        self.httpmodule.uploadSensorData("weightBowl",weight_value) # Bowl Weight

    """
    TODO: Implement emergency stop to all 12v components
    """
    def monitor_waste_water_level(self):
        self.waste_water_level_sensor.monitor_water_level()

    def monitor_turbidity_level(self):
        while self.monitoring:
            turbidity_value = self.turbidity_sensor.read_turbidity()
            print(f"Monitoring - Turbidity Level: {turbidity_value}")
            ntu_id = self.turbidity_sensor.id
            weightValue = self.readWeight.read_weight()
            self.httpmodule.uploadSensorData("weightBowl",weightValue)
            self.httpmodule.uploadSensorData(ntu_id,turbidity_value)

            sleep(1)

    def start_monitoring(self):
        self.wifi_conn.start_real_time_update()

        self.turbidity_thread = threading.Thread(target=self.monitor_turbidity_level)
        self.turbidity_thread.daemon = True
        self.turbidity_thread.start()

        self.rfid_thread = threading.Thread(target=self.rfid_module.read_rfid)
        self.rfid_thread.daemon = True
        self.rfid_thread.start()

        self.monitor_waste_water_level()

        if self.turbidity_sensor.read_turbidity() >= 4.5:
            self.drain_bowl()

    def on_message(self, client, userdata, message):
        topic = message.topic
        payload = message.payload.decode('utf-8')

        if topic == "remotecommand":
            if payload == "0":
                print("No command specified.")
            elif payload == "changewater":
                self.drain_bowl()
                time.sleep(2)
                self.mqtt_client.send_message("remotecommand", "0")
            elif payload == "refillwater":
                self.drain_bowl()
                time.sleep(2)
                self.mqtt_client.send_message("remotecommand", "0")
            elif payload == "restartfeeder":
                self.mqtt_client.send_message("remotecommand", "0")
                os.system("reboot")
            else:
                print(f"Unknown command received: {payload}")

    # Bowl capacity is 2 Litres and drained within 35 seconds.
    def drain_bowl(self):
        print("Draining water...")
        start_time = time()

        # Start the pump and open the valve
        self.pump.start()
        self.bowl_valve.open()

        while time() - start_time < 35:
            # Use inverse for waste tank
            if not self.waste_water_level_sensor.is_low():
                print("Waste tank is full! Please empty the tank.")
                print("Stopping pump and closing valve...")
                self.pump.stop()
                self.bowl_valve.close()
                return

            sleep(1)

        print("Stopping pump and closing valve...")
        self.pump.stop()
        self.bowl_valve.close()


    def cleanup(self):
        self.monitoring = False
        if hasattr(self, 'turbidity_thread') and self.turbidity_thread.is_alive():
            self.turbidity_thread.join()
        self.waste_water_level_sensor.cleanup()
        self.rfid_module.cleanup()
        self.pump.cleanup()
        self.wifi_conn.stop_real_time_update()

if __name__ == "__main__":
    backendAddr = "203.29.240.135"

    mqtt_client = mqttModule.MQTTModule(server=backendAddr, port=1883)
    mqtt_client.connect()
    turbidity_sensor = TurbidityModule(id="turbiditysensor", sensor_channel=0) # Install sensor on A0 on ADS115 (Occupied Pin 2 and 3)
    reservoir_valve = ValveModule(pin=20)
    httpmodule = httpModule.HTTPModule(server=backendAddr)
    wifi_conn = wificonn.WiFiConn(update_interval=5, api_url=f'http://{backendAddr}:5000/update_wificonn')
    waste_water_level_sensor = WaterLevelModule(in_pin=22, mode_pin=27, sensor_location="waterlevelwaste")
    weight_bowl = readWeight(iic_mode=0x03, iic_address=0x64, calibration_value=223.7383270263672)
    weight_bowl.begin()
    rfid_module = RFIDModule(server=backendAddr,water_weight=weight_bowl)
    pump = PumpModule(pin=16)
    bowl_valve = ValveModule(pin=21)
    # Note: The ID or sensor_location must align with Remote API defined. For more info, please visit: https://github.com/xosadmin/cits5506/blob/main/routes.py
    
    try:
        water_feeder = WaterFeeder(
            pump_arg = pump,
            mqtt_client=mqtt_client,
            waste_water_level_sensor_arg=waste_water_level_sensor,
            turbidity_sensor=turbidity_sensor,
            reservoir_valve=reservoir_valve,
            rfid_module=rfid_module,
            wifi_conn=wifi_conn,
            httpmodule=httpmodule,
            readWeight=weight_bowl,
            bowl_valve_arg=bowl_valve
        )
        water_feeder.start_monitoring()
        while True:
            sleep(1)

    except KeyboardInterrupt:
        print("Exiting program...")

    finally:
        water_feeder.cleanup()
        mqtt_client.disconnect()
