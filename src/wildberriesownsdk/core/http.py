from json import JSONDecodeError
from typing import Union, TypeVar

import httpx
from loguru import logger


HTTPResponse = TypeVar("HTTPResponse", bound=httpx.Response)


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

    logger.info(f"Status code {response.status_code}. Response json: {resp_json}")
