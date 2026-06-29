import logging
from logging.handlers import RotatingFileHandler

from config import settings


_LOGGER_INITIALIZED = False


def init_logging():
    global _LOGGER_INITIALIZED
    if _LOGGER_INITIALIZED:
        return

    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    _LOGGER_INITIALIZED = True


def get_logger(name):
    init_logging()
    return logging.getLogger(name)
