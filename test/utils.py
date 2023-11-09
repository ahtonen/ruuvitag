import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ruuvi_measurements = {
    "sauna": {
        "data_format": 5,
        "humidity": 44.11,
        "temperature": 22.27,
        "pressure": 994.92,
        "acceleration": 1018.3044731316857,
        "acceleration_x": 964,
        "acceleration_y": -328,
        "acceleration_z": -8,
        "tx_power": 4,
        "battery": 3038,
        "movement_counter": 59,
        "measurement_sequence_number": 58830,
        "mac": "edbd47da64d4",
        "rssi": -67,
    },
    "balcony": {
        "data_format": 5,
        "humidity": 92.89,
        "temperature": 7.98,
        "pressure": 996.13,
        "acceleration": 1018.6186725168551,
        "acceleration_x": 144,
        "acceleration_y": 1008,
        "acceleration_z": -28,
        "tx_power": 4,
        "battery": 2964,
        "movement_counter": 101,
        "measurement_sequence_number": 58448,
        "mac": "c950b17da88f",
        "rssi": -76,
    },
}


class MissingEnvironmentVariable(Exception):
    pass


def get_env_var(var_name):
    """
    Try to return environment variable.
    """
    try:
        return os.environ[var_name]
    except KeyError:
        raise MissingEnvironmentVariable(f"{var_name} does not exist")
