import httpx


def request(self, *args, **kwargs) -> httpx.Response:
    return httpx.request(*args, **kwargs)


async def async_request(self, *args, **kwargs) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.request(*args, **kwargs)
