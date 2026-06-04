import asyncio
from typing import Union


async def async_wait(sleep_time: Union[int, float]) -> None:
    await asyncio.sleep(sleep_time)
