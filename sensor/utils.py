import logging
import os

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
