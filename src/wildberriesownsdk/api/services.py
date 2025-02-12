import httpx


class RequestService:
    timeout = httpx.Timeout(15.0, connect=30)

    def request(self, *args, **kwargs) -> httpx.Response:
        request_kwargs = self.update_kwargs_with_timeout(kwargs)
        return httpx.request(*args, **request_kwargs)

    async def async_request(self, *args, **kwargs) -> httpx.Response:
        request_kwargs = self.update_kwargs_with_timeout(kwargs)
        async with httpx.AsyncClient() as client:
            return await client.request(*args, **request_kwargs)

    @classmethod
    def update_kwargs_with_timeout(cls, request_kwargs: dict) -> dict:
        request_kwargs.setdefault("timeout", cls.timeout)
        return request_kwargs
