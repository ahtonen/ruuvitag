import ast
import logging
import logging.handlers
import os
import sys
import time

from multiprocessing import Process, Queue

import boto3
import pytz
import requests
from aws_timestream import write_ruuvi_record
from botocore.config import Config
from ruuvitag_sensor.ruuvi import RuuviTagSensor
from utils import ISO8601Formatter, MissingEnvironmentVariable, get_env_var


# configure root logger
logger = logging.getLogger()
if os.environ.get("DEBUG"):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# logging.getLogger("ruuvitag_sensor.ruuvi").setLevel(logging.DEBUG)
# logging.getLogger("ruuvitag_sensor.adapters.nix_hci").setLevel(logging.DEBUG)

iso_formatter = ISO8601Formatter("%(asctime)s %(levelname)s in %(module)s: %(message)s")

console_handler = logging.StreamHandler(sys.stdout)
# drop timestamps for Balena cloud provides switch between local and utc
if os.environ.get("BALENA"):
    console_handler.setFormatter(
        ISO8601Formatter("%(levelname)s in %(module)s: %(message)s")
    )
else:
    console_handler.setFormatter(iso_formatter)

file_handler = logging.handlers.RotatingFileHandler(
    "/mnt/log/sensor.log", maxBytes=(1048576 * 2), backupCount=5
)
file_handler.setFormatter(iso_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


region = get_env_var("AWS_REGION")
ENABLE_AWS_WRITE = True
write_interval = ast.literal_eval(get_env_var("AWS_WRITE_INTERVAL"))
max_empty_queue_count = ast.literal_eval(get_env_var("MAX_EMPTY_QUEUE_COUNT"))

try:
    ruuvitag_mac_aliases = ast.literal_eval(get_env_var("RUUVITAG_MAC_ALIASES"))
    if len(ruuvitag_mac_aliases.keys()) == 0:
        logger.error("Empty of malformed dictionary in RUUVITAG_MAC_ALIASES.")
        exit(1)

except MissingEnvironmentVariable as e:
    logger.warning(
        "%s, defaulting to allow all ruuvitag macs. AWS write disable, revert to debug mode.",
        e,
    )
    ENABLE_AWS_WRITE = False
    logger.setLevel(logging.DEBUG)


def validate_data(data: tuple):
    """
    Validate record. All keys must have 'not None' value.
    """
    for _, value in data[1].items():
        if value is None:
            return False

    return True


def restart_container():
    """
    Ask supervisor to restart container. Essentially a self recovery attempt.
    """
    headers = {"Content-Type": "application/json"}
    data = {"appId": get_env_var("BALENA_APP_ID")}
    url = "{}/v1/restart?apikey={}".format(
        get_env_var("BALENA_SUPERVISOR_ADDRESS"),
        get_env_var("BALENA_SUPERVISOR_API_KEY"),
    )
    # should return status code, but since container will restart, it doesn't
    return requests.post(url, json=data, headers=headers)


def ruuvi_event_loop(q: Queue):
    """
    Put received measurements from allowed MACs to queue.
    """

    def handle_data(found_data):
        try:
            if validate_data(found_data):
                logger.debug("PUT %s", found_data)
                q.put(found_data, True, write_interval)

        except Exception as e:
            logger.warning(e)

    if ENABLE_AWS_WRITE:
        RuuviTagSensor.get_data(handle_data, list(ruuvitag_mac_aliases.keys()))
    else:
        RuuviTagSensor.get_data(handle_data)


if __name__ == "__main__":
    q = Queue()  # FIFO queue
    p = Process(target=ruuvi_event_loop, args=(q,))  # MUST be with comma

    session = boto3.Session()
    write_client = session.client(
        "timestream-write",
        config=Config(
            region_name=region,
            read_timeout=20,
            max_pool_connections=5000,
            retries={"max_attempts": 10},
        ),
    )

    p.start()

    try:
        empty_queue_counter = 0

        while True:
            now = time.time()

            if not q.empty():
                # Reset consecutive empty queue counter
                empty_queue_counter = 0
                # Empty process queue by reading everything
                received_measurements = []
                while not q.empty():
                    received_measurements.append(q.get())

                # Get latest measurement for each sensor, report counts
                latest_measurements = {}
                counts = {}
                for m in received_measurements:
                    mac = m[0]
                    latest_measurements[mac] = m[1]

                    if not mac in counts:
                        counts[mac] = 1
                    else:
                        counts[mac] += 1
                logger.debug("COUNTS: %s", counts)
                logger.debug("FLUSH: %s", latest_measurements)

                # Write to AWS only if mac aliases are provided
                if ENABLE_AWS_WRITE:
                    for mac, measurement in latest_measurements.items():
                        write_ruuvi_record(
                            write_client, ruuvitag_mac_aliases[mac], measurement
                        )

            else:
                empty_queue_counter += 1
                logger.warning("Queue was empty")

            if empty_queue_counter >= max_empty_queue_count:
                logger.warning(
                    "Max empty queue count exceeded. Restarting container..."
                )
                response = restart_container()

            # wait
            while (time.time() - now) < write_interval:
                time.sleep(0.001)

    except KeyboardInterrupt:
        logger.info("\nExiting (Ctrl + C).")
        p.join()
