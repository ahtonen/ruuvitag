import logging
import os
from datetime import datetime

import pytz

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


class ISO8601Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return (
            datetime.fromtimestamp(record.created).astimezone(pytz.utc)
            # .astimezone(pytz.timezone("Europe/Helsinki"))
            .isoformat(timespec="milliseconds")
        )