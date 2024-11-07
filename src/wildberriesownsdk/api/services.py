import abc

import httpx


class RequestService:

    @abc.abstractmethod
    def get_auth_headers(self) -> dict:
        raise NotImplementedError("get_auth_headers method have to be implemented")

    def request(self, *args, **kwargs):
        return httpx.request(*args, **self._set_headers(**kwargs))

    async def async_request(self, *args, **kwargs):
        async with httpx.AsyncClient() as client:
            return await client.request(*args, **self._set_headers(**kwargs))

    def _set_headers(self, **request_kwargs) -> dict:
        headers = request_kwargs.get("headers")
        if headers is None:
            request_kwargs["headers"] = self.get_auth_headers()
        else:
            headers.update(**self.get_auth_headers())
            request_kwargs["headers"] = headers

        return request_kwargs
