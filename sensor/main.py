import ast
import logging
import os
import sys
import time
from multiprocessing import Process, Queue

from ruuvitag_sensor.ruuvi import RuuviTagSensor

log_format_str = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
# drop timestamp out in when in Balena environment
if os.environ.get("BALENA"):
    log_format_str = "%(levelname)s in %(module)s: %(message)s"

logging.basicConfig(stream=sys.stdout, format=log_format_str, level=logging.INFO)
# logging.getLogger("ruuvitag_sensor.ruuvi").setLevel(logging.DEBUG)
# logging.getLogger("ruuvitag_sensor.adapters.nix_hci").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

ruuvitag_mac_aliases = {}
if os.environ.get("RUUVITAG_MAC_ALIASES"):
    ruuvitag_mac_aliases = ast.literal_eval(os.environ["RUUVITAG_MAC_ALIASES"])
else:
    logger.warning(
        "'RUUVITAG_MAC_ALIASES' environment variable missing. Defaulting to '{}'."
    )

location = "not set"
if os.environ.get("LOCATION"):
    location = ast.literal_eval(os.environ["LOCATION"])
else:
    logger.warning("'LOCATION' environment variable missing. Defaulting to 'not set'.")

write_interval = 60
if os.environ.get("AWS_WRITE_INTERVAL"):
    write_interval = ast.literal_eval(os.environ["AWS_WRITE_INTERVAL"])
else:
    logger.warning(
        "'AWS_WRITE_INTERVAL' environment variable missing. Defaulting to 60 seconds."
    )


def ruuvi_event_loop(q: Queue):
    """
    Put received measurements from allowed MACs to queue.
    """

    def handle_data(found_data):
        try:
            logger.debug(f"PUT {found_data}")
            q.put(found_data, True, write_interval)

        except Exception as e:
            logger.warning(e)

    RuuviTagSensor.get_data(handle_data, ruuvitag_mac_aliases.keys())


if __name__ == "__main__":
    q = Queue()  # FIFO queue
    p = Process(target=ruuvi_event_loop, args=(q,))  # MUST be with comma

    if not ruuvitag_mac_aliases:
        logger.info("Alias dictionary empty, all MACs are valid.")

    p.start()

    try:
        while True:
            now = time.time()

            if not q.empty():
                received_measurements = []
                while not q.empty():
                    received_measurements.append(q.get())

                latest_measurements = {}
                for m in received_measurements:
                    mac = m[0]
                    latest_measurements[ruuvitag_mac_aliases[mac]] = m[1]

                logger.info(f"FLUSH: {latest_measurements}")
            else:
                logger.warning("Queue was empty")

            # wait
            while (time.time() - now) < write_interval:
                time.sleep(0.001)

    except KeyboardInterrupt:
        logger.info("\nExiting (Ctrl + C).")
        p.join()
