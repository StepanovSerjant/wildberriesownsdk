import datetime
from http import HTTPMethod

from wildberriesownsdk.api.actions.base import WBAPIAction


class MarketPlaceAPIDetailsMixin:
    api_url = "https://marketplace-api.wildberries.ru/api"
    api_version = "v3"


class OrdersAPIAction(MarketPlaceAPIDetailsMixin, WBAPIAction):
    name = "Получить список сборочных заданий"
    description = (
        "Возвращает список всех сборочных заданий у продавца на данный момент"
    )

    path = "orders"
    method = HTTPMethod.GET

    has_pagination = True
    collect_all_pages_if_paginated = False

    def __init__(
        self,
        api_connector,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
        page: int = 1,
        per_page: int = 100,
    ):
        super().__init__(api_connector, page=page, per_page=per_page)
        self._date_from = date_from
        self._date_to = date_to

    def get_query_params(self):
        query_params = super().get_query_params()
        date_query_params = {
            "dateFrom": int(self._date_from.timestamp()),
            "dateTo": int(self._date_to.timestamp()),
        }
        query_params.update(date_query_params)
        return query_params


class NewOrdersAPIAction(MarketPlaceAPIDetailsMixin, WBAPIAction):
    name = "Получить список новых сборочных заданий"
    description = "Возвращает список всех новых сборочных заданий у продавца на данный момент"

    path = "orders/new"
    method = HTTPMethod.GET
    has_pagination = True

    root_data_field = "orders"


class OrdersStatusesAPIAction(MarketPlaceAPIDetailsMixin, WBAPIAction):
    name = "Получить статусы сборочных заданий"
    description = (
        "Возвращает статусы сборочных заданий по переданному списку идентификаторов сборочных заданий."
        "supplierStatus - статус сборочного задания, триггером изменения которого является сам продавец."
    )

    path = "orders/status"
    method = HTTPMethod.GET

    root_data_field = "orders"

    def __init__(
        self, api_connector, body: dict, page: int = 1, per_page: int = 100
    ):
        super().__init__(api_connector, page=page, per_page=per_page)
        self._request_body = body

    def get_body(self) -> dict:
        return self._request_body


class GetSupplyAPIAction(MarketPlaceAPIDetailsMixin, WBAPIAction):
    name = "Получить информацию о поставке"
    description = "Возвращает информацию о поставке."

    path = "supplies"
    method = HTTPMethod.PATCH

    def __init__(
        self, api_connector, supply_id: str, page: int = 1, per_page: int = 100
    ):
        super().__init__(api_connector, page=page, per_page=per_page)
        self.supply_id = supply_id

    def get_url(self) -> str:
        url = super().get_url()
        return "/".join([url, self.supply_id])


class CreateSupplyAPIAction(MarketPlaceAPIDetailsMixin, WBAPIAction):
    name = "Создать новую поставку"

    path = "supplies"
    method = HTTPMethod.POST

    root_data_field = "id"

    def __init__(
        self, api_connector, name: str, page: int = 1, per_page: int = 100
    ):
        super().__init__(api_connector, page=page, per_page=per_page)
        self._body_name = name

    def get_body(self) -> dict:
        return {"name": self._body_name}


class OrdersToSupplyAPIAction(MarketPlaceAPIDetailsMixin, WBAPIAction):
    name = "Добавить к поставке сборочное задание"
    description = "Добавляет к поставке сборочное задание и переводит его в статус confirm ('На сборке')"

    path = "supplies/{supply_id}/orders/{order_id}"
    method = HTTPMethod.PATCH

    def __init__(
        self,
        api_connector,
        supply_id: str,
        order_id: int,
        page: int = 1,
        per_page: int = 100,
    ):
        super().__init__(api_connector, page=page, per_page=per_page)
        self.supply_id = supply_id
        self.order_id = order_id

    def get_url(self):
        query_map = {"supply_id": self.supply_id, "order_id": self.order_id}
        return super().get_url().format(**query_map)
