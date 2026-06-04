from abc import ABCMeta
from http import HTTPMethod, HTTPStatus
from typing import Any, Coroutine, Dict, Optional, Union
from urllib import parse

from camel_converter import dict_to_snake
from deepmerge import always_merger

from wildberriesownsdk.api.constants import MAX_PER_PAGE_VALUE
from wildberriesownsdk.api.exceptions import (
    GettingDataFromAPIException,
    ThrottlingAPIException,
)
from wildberriesownsdk.core.http import (
    HTTPResponse,
    async_perform_request,
    create_timeout_instance,
    log_response,
    perform_request,
)


class WBAPIAction(metaclass=ABCMeta):
    api_url: str
    api_version: str

    name: str
    description: Optional[str] = None

    method: HTTPMethod = HTTPMethod.GET
    path: Optional[str] = None
    timeout: Union[int, float] = 15.0

    has_pagination: bool = False
    collect_all_pages_if_paginated: bool = True
    root_data_field: Optional[str] = None

    def __init__(
        self, api_connector, page: int = 1, per_page: int = 100
    ) -> None:
        if per_page > MAX_PER_PAGE_VALUE:
            raise ValueError(
                f"per_page argument should be in range 1-{MAX_PER_PAGE_VALUE}"
            )

        self.api_key = api_connector.api_key
        self.api_scopes = api_connector.scopes
        self.page = page  # 0 value - disable pagination
        self.per_page = per_page
        self.last_response: Optional[HTTPResponse] = None

    def __str__(self) -> str:
        return (
            f"WB Сервис {self.name}\n{self.description}"
            if self.description
            else f"WB Сервис {self.name}"
        )

    @property
    def pagination_query_params(self) -> Dict[str, int]:
        if self.has_pagination:
            return {
                "limit": self.per_page,
                "next": self.page,
            }
        return {}

    def get_url(self) -> str:
        url = f"{self.api_url}/{self.api_version}/{self.path}"
        query_params = self.get_query_params()
        if query_params:
            url_query = parse.urlencode(query_params)
            return f"{url}?{url_query}"

        return url

    def get_auth_headers(self) -> Dict[str, str]:
        return {"Authorization": self.api_key, "accept": "application/json"}

    def get_body(self) -> Dict[str, Any]:
        return {}

    def get_files(self) -> Dict[str, Any]:
        return {}

    def get_query_params(self) -> Dict[str, Any]:
        return self.pagination_query_params

    def do(self) -> Any:
        if self.has_pagination and self.collect_all_pages_if_paginated:
            response_data = self.get_merged_response_data()
        else:
            response = self.perform_request()
            response_data = self.get_response_data(response)

        snaked_response_data = dict_to_snake(response_data)
        return (
            snaked_response_data[self.root_data_field]
            if self.root_data_field
            else snaked_response_data
        )

    async def async_do(self) -> Any:
        if self.has_pagination:
            response_data = self.get_merged_response_data()
        else:
            response = await self.async_perform_request()
            response_data = self.get_response_data(response)

        snaked_response_data = dict_to_snake(response_data)
        return (
            snaked_response_data[self.root_data_field]
            if self.root_data_field
            else snaked_response_data
        )

    def get_merged_response_data(self) -> Any:
        merged_response_data = {}

        start_page = self.page
        while start_page:
            response = self.perform_request()
            response_data = self.get_response_data(response)

            next_page = response_data.pop("next", 0)
            merged_response_data = always_merger.merge(
                merged_response_data.copy(), response_data
            )

            if next_page and next_page > self.page:
                self.page = next_page
            else:
                break

        return merged_response_data

    def perform_request(self) -> HTTPResponse:
        request_kwargs = self.get_request_kwargs()
        self.last_response = perform_request(**request_kwargs)
        log_response(self.last_response)
        return self.last_response

    async def async_perform_request(self) -> HTTPResponse:
        request_kwargs = self.get_request_kwargs()
        self.last_response = await async_perform_request(**request_kwargs)
        log_response(self.last_response)
        return self.last_response

    def get_request_kwargs(self) -> Dict[str, Any]:
        request_kwargs = {
            "method": self.method,
            "url": self.get_url(),
            "headers": self.get_auth_headers(),
        }
        if self.method == HTTPMethod.POST and (files_data := self.get_files()):
            request_kwargs["files"] = files_data
        else:
            request_kwargs["json"] = self.get_body()

        if self.timeout:
            request_kwargs["timeout"] = create_timeout_instance(self.timeout)

        return request_kwargs

    def get_response_data(self, response: Union[HTTPResponse, Coroutine]):
        response_status_code = response.status_code
        if HTTPStatus.OK <= response_status_code < HTTPStatus.BAD_REQUEST:
            return (
                {}
                if response_status_code == HTTPStatus.NO_CONTENT
                else response.json()
            )
        elif response_status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise ThrottlingAPIException(
                f"Сервис {self.name} не смог получить данные.\n Слишком много запросов на единицу времени"
            )
        else:
            raise GettingDataFromAPIException(
                f"Сервис {self.name} не смог получить данные.\n Статус код ответа сервера {response_status_code}"
            )
