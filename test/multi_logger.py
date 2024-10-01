from datetime import datetime
import logging
import logging.handlers
import os
import sys
import time
import pytz


class ISO8601Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return (
            datetime.fromtimestamp(record.created).astimezone(pytz.utc)
            # .astimezone(pytz.timezone("Europe/Helsinki"))
            .isoformat(timespec="microseconds")
        )


logger = logging.getLogger(__name__)
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
    "app.log", maxBytes=(1048576 * 2), backupCount=5
)
file_handler.setFormatter(iso_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

if __name__ == "__main__":
    try:
        count = 0
        while True:
            logger.info("Log message %i", count)
            logger.debug("Log message %i", count)
            count += 1
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("\nExiting (Ctrl + C).")
