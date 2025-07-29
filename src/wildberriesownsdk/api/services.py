import abc
from typing import Dict, Any

import httpx


class RequestService:

    @abc.abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        raise NotImplementedError("get_auth_headers method have to be implemented")

    def request(self, *args, **kwargs) -> httpx.Response:
        return httpx.request(*args, **self._set_headers(**kwargs))

    async def async_request(self, *args, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            return await client.request(*args, **self._set_headers(**kwargs))

    def _set_headers(self, **request_kwargs) -> Dict[str, Any]:
        headers = request_kwargs.get("headers")
        if headers is None:
            request_kwargs["headers"] = self.get_auth_headers()
        else:
            headers.update(**self.get_auth_headers())
            request_kwargs["headers"] = headers

        return request_kwargs
