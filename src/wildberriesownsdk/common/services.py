import httpx


class RequestService:
    timeout = httpx.Timeout(15.0, connect=30)

    def request(self, *args, **kwargs) -> httpx.Response:
        return httpx.request(*args, **kwargs)

    async def async_request(self, *args, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            return await client.request(*args, **kwargs)
