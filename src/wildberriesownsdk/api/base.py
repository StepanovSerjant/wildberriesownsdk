from typing import Any, Coroutine, Union
from urllib import parse

import httpx
from camel_converter import dict_to_snake
from deepmerge import always_merger

from wildberriesownsdk.api import config
from wildberriesownsdk.api.services import RequestService
from wildberriesownsdk.common.exceptions import (
    GettingDataFromAPIException,
    ThrottlingAPIException,
)
from wildberriesownsdk.common.utils import log_response


class WBAPIAction(RequestService):
    name = "default"
    help_text = "text about service"

    method = ""
    path = ""
    scope = None

    paginated = False
    data_field = ""

    def __init__(self, api_connector, page: int = 1):
        self.api_key = api_connector.api_key
        self.api_scopes = api_connector.scopes
        self.page = page  # 0 value - disable pagination

    def __str__(self) -> str:
        return (
            f"WB Сервис {self.name}\n{self.help_text}"
            if self.help_text
            else f"WB Сервис {self.name}"
        )

    @property
    def pagination_query_params(self) -> dict:
        if self.paginated:
            return {
                "limit": 100,
                "next": self.page,
            }
        return {}

    def do(self) -> Any:
        if self.paginated:
            response_data = self.get_merged_response_data()
        else:
            response = self.perform_request()
            response_data = self.get_response_data(response)

        snaked_response_data = dict_to_snake(response_data)
        return (
            snaked_response_data[self.data_field]
            if self.data_field
            else snaked_response_data
        )

    async def async_do(self) -> Any:
        if self.paginated:
            response_data = self.get_merged_response_data()
        else:
            response = await self.async_perform_request()
            response_data = self.get_response_data(response)

        snaked_response_data = dict_to_snake(response_data)
        return (
            snaked_response_data[self.data_field]
            if self.data_field
            else snaked_response_data
        )

    def get_merged_response_data(self):
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

    def perform_request(self) -> httpx.Response:
        request_kwargs = self.get_request_kwargs()
        response = self.request(**request_kwargs)
        log_response(response)
        return response

    async def async_perform_request(self) -> httpx.Response:
        request_kwargs = self.get_request_kwargs()
        response = await self.async_request(**request_kwargs)
        log_response(response)
        return response

    def get_auth_headers(self) -> dict:
        return {"Authorization": self.api_key, "accept": "application/json"}

    def get_body(self) -> dict:
        return {}

    def get_files(self) -> dict:
        return {}

    def get_url(self) -> str:
        if self.scope not in config.API_AVAILABLE_SCOPES:
            available_scopes_str = ", ".join(config.API_AVAILABLE_SCOPES)
            raise ValueError(f"Invalid scope. Use any of: {available_scopes_str}")

        api_url = config.API_SCOPE_DATA_MAP[self.scope]["url"]
        api_version = config.API_SCOPE_DATA_MAP[self.scope]["api_version"]
        url = f"{api_url}/{api_version}/{self.path}"

        query_params = self.get_query_params()
        if query_params:
            url_query = parse.urlencode(query_params)
            return f"{url}?{url_query}"

        return url

    def get_query_params(self) -> dict:
        return self.pagination_query_params

    def get_request_kwargs(self) -> dict:
        request_kwargs = {
            "method": self.method,
            "url": self.get_url(),
            "headers": self.get_auth_headers(),
        }
        if self.method == "POST" and (files_data := self.get_files()):
            request_kwargs["files"] = files_data
        else:
            request_kwargs["json"] = self.get_body()

        if self.timeout:
            request_kwargs["timeout"] = self.timeout

        return request_kwargs

    def get_response_data(self, response: Union[httpx.Response, Coroutine]):
        response_status_code = response.status_code
        if httpx.codes.OK <= response_status_code < httpx.codes.BAD_REQUEST:
            return (
                {}
                if response_status_code == httpx.codes.NO_CONTENT
                else response.json()
            )
        elif response_status_code == httpx.codes.TOO_MANY_REQUESTS:
            raise ThrottlingAPIException(
                f"Сервис {self.name} не смог получить данные.\n Слишком много запросов на единицу времени"
            )
        else:
            raise GettingDataFromAPIException(
                f"Сервис {self.name} не смог получить данные.\n Статус код ответа сервера {response_status_code}"
            )
