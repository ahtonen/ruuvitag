import time
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import logging
import ast
import os, sys
from utils import SimpleMeasurement
from collections.abc import Sequence
from multiprocessing import Process
from multiprocessing.sharedctypes import Value, Array

logging.basicConfig(
    stream=sys.stdout,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    level=logging.INFO,
)
# logging.getLogger("ruuvitag_sensor.ruuvi").setLevel(logging.DEBUG)
# logging.getLogger("ruuvitag_sensor.adapters.nix_hci").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

allowed_macs = ast.literal_eval(os.environ["RUUVITAG_MACS_TO_LISTEN"])
ruuvitag_macs = ast.literal_eval(os.environ["RUUVITAG_MAC_ALIASES"])


def ruuvi_event_loop(data: SimpleMeasurement):
    def handle_data(found_data):
        sensor_name = found_data[0]

        try:
            sensor_name = ruuvitag_macs[found_data[0]]
            logger.debug(f"{sensor_name}: {found_data[1]}")
            data[1].temperature = found_data[1]["temperature"]

        except Exception as e:
            logger.warn(
                f"MAC {sensor_name} not found in RUUVITAG_MAC_ALIASES environment variable. -- {e}"
            )

    RuuviTagSensor.get_data(handle_data, allowed_macs)


if __name__ == "__main__":
    #data = Value(SimpleMeasurement, 0.0, lock=True)
    data = Array(SimpleMeasurement, len(allowed_macs), lock=True)
    write_interval = 15 # seconds

    p = Process(target=ruuvi_event_loop, args=(data,)) # MUST be with comma
    try:
        p.start()

        while True:
            now = time.time()

            # write temperature
            logger.info(f"Write loop, TEMP {data[0].temperature}")

            # wait
            while (time.time() - now) < write_interval:
                time.sleep(0.001)

    except KeyboardInterrupt:
        logger.info("\nExiting (Ctrl + C).")
        p.join()
