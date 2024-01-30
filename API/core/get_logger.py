from logging import getLogger
from logging.config import dictConfig

from core.config import get_settings


SETTINGS = get_settings()

dictConfig(SETTINGS.LOGGING)


def get_logger(name):
    return getLogger(name)
