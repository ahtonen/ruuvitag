import logging
from ctypes import Structure, c_int8, c_uint8, c_uint16, c_float

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Measurement(Structure):
    """
    Ruuvi data format 5
    Skip acceleration components, mac and rssi.
    """

    _fields_ = [
        ("data_format", c_uint8),
        ("humidity", c_float),  # RH percent
        ("temperature", c_float),  # Celsius
        ("pressure", c_float),  # mBar
        ("acceleration", c_float),  # total acceleration m/s2
        ("tx_power", c_int8),  # dBm
        ("battery", c_uint16),  # millivolts
        ("measurement_sequence_number", c_uint16),
    ]


class SimpleMeasurement(Structure):
    _fields_ = [
        ("temperature", c_float)  # Celsius
    ]
