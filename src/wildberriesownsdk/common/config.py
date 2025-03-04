import sys

import pytz
from loguru import logger

BASE_MARKETPLACE_API_URL = "https://marketplace-api.wildberries.ru/api"
BASE_CONTENT_API_URL = "https://content-api.wildberries.ru/content"

API_VERSION = "v3"
CONTENT_API_VERSION = "v3"

API_DATABASE_TZ = pytz.UTC
API_DATABASE_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

logger.add(
    sys.stdout,
    format="{time} {level} {message}",
    level="INFO",
    filter=lambda record: record["level"].no in [20, 40],
    colorize=True,
    backtrace=True,
    diagnose=True,
)
