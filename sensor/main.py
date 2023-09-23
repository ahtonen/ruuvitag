from ruuvitag_sensor.ruuvi import RuuviTagSensor
import ast
import os

allowed_macs = ast.literal_eval(os.environ["RUUVITAG_MACS_TO_LISTEN"])
ruuvitag_macs = ast.literal_eval(os.environ["RUUVITAG_MAC_ALIASES"])

def handle_data(found_data):
    sensor_name = found_data[0]

    try:
        sensor_name = ruuvitag_macs[found_data[0]]
        print(f"{sensor_name}: {found_data[1]}")

    except Exception as e:        
        print(f"WARNING: MAC {sensor_name} not found in RUUVITAG_MAC_ALIASES environment variable. -- {e}")


if __name__ == "__main__":    
    RuuviTagSensor.get_data(handle_data, allowed_macs)
