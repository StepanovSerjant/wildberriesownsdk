import sys

from loguru import logger

# TODO change to structlog
logger.add(
    sys.stdout,
    format="{time} {level} {message}",
    level="INFO",
    filter=lambda record: record["level"].no in [20, 40],
    colorize=True,
    backtrace=True,
    diagnose=True,
)
