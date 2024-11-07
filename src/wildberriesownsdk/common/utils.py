import datetime
import functools
import time
from json import JSONDecodeError
from typing import Optional, Any

import pytz
import httpx

from wildberriesownsdk.common.config import logger


def get_tz(tz_name: str):
    return pytz.timezone(tz_name)


def get_current_dtm(tz_name: Optional[str]) -> datetime.datetime:
    tz = get_tz(tz_name) if tz_name else pytz.UTC
    return datetime.datetime.now().astimezone(tz=tz)


def log_response(response: httpx.Response) -> None:
    logger.info(f"Requested resource ({response.url}).")

    try:
        resp_json = response.json()
    except JSONDecodeError:
        resp_json = {}

    logger.info(
        f"Status code {response.status_code}. Response json: {resp_json}"
    )


def retry(target_value: Any, tries: int = 1, delay: int = 1):
    def func_exc(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_value = None
            for i in range(tries):
                last_value = func(*args, **kwargs)
                if target_value == last_value:
                    break

                if i + 1 < tries:
                    time.sleep(delay)

            return last_value

        return wrapper

    return func_exc

