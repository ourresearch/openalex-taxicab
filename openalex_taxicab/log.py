import logging
import sys

def _make_logger():
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    return logger

LOGGER = _make_logger()
