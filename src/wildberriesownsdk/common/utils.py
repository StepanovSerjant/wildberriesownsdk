import asyncio
import datetime
from json import JSONDecodeError
from typing import Optional, Union

import httpx
import pytz
from pytz.tzinfo import StaticTzInfo

from wildberriesownsdk.common.config import logger


def get_tz(tz_name: str) -> StaticTzInfo:
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

    logger.info(f"Status code {response.status_code}. Response json: {resp_json}")


async def async_wait(sleep_time: Union[int, float]) -> None:
    await asyncio.sleep(sleep_time)
