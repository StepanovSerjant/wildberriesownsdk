import logging
from json import JSONDecodeError
from typing import TypeVar, Union

import httpx

HTTPResponse = TypeVar("HTTPResponse", bound=httpx.Response)
logger = logging.getLogger(__name__)


def perform_request(*args, **kwargs) -> HTTPResponse:
    return httpx.request(*args, **kwargs)


async def async_perform_request(*args, **kwargs) -> HTTPResponse:
    async with httpx.AsyncClient() as client:
        return await client.request(*args, **kwargs)


def create_timeout_instance(timeout: Union[float, int]) -> httpx.Timeout:
    return httpx.Timeout(timeout, connect=timeout * 2)


def log_response(response: HTTPResponse) -> None:
    logger.info(f"Requested resource ({response.url}).")

    try:
        resp_json = response.json()
    except JSONDecodeError:
        resp_json = {}

    logger.info(
        f"Status code {response.status_code}. Response json: {resp_json}"
    )
