import datetime

from wildberriesownsdk.api.base import WBAPIAction


class OrdersAPIAction(WBAPIAction):
    name = "Получить список сборочных заданий"
    help_text = (
        "Возвращает список всех сборочных заданий у продавца на данный момент"
    )

    path = "orders"
    method = "GET"

    paginated = True
    merge_data_if_paginated = False

    def __init__(self, api_connector, date_from: datetime.datetime, date_to: datetime.datetime, page: int = 1, per_page: int = 100):
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


class NewOrdersAPIAction(WBAPIAction):
    name = "Получить список новых сборочных заданий"
    help_text = (
        "Возвращает список всех новых сборочных заданий у продавца на данный момент"
    )

    path = "orders/new"
    method = "GET"
    paginated = True

    data_field = "orders"


class OrdersStatusesAPIAction(WBAPIAction):
    name = "Получить статусы сборочных заданий"
    help_text = (
        "Возвращает статусы сборочных заданий по переданному списку идентификаторов сборочных заданий."
        "supplierStatus - статус сборочного задания, триггером изменения которого является сам продавец."
    )

    path = "orders/status"
    method = "POST"

    data_field = "orders"

    def __init__(self, api_connector, body: dict, page: int = 1, per_page: int = 100):
        super().__init__(api_connector, page=page, per_page=per_page)
        self._request_body = body

    def get_body(self) -> dict:
        return self._request_body


class GetSupplyAPIAction(WBAPIAction):
    name = "Получить информацию о поставке"
    help_text = "Возвращает информацию о поставке."

    path = "supplies"
    method = "GET"

    def __init__(self, api_connector, supply_id: str, page: int = 1, per_page: int = 100):
        super().__init__(api_connector, page=page, per_page=per_page)
        self.supply_id = supply_id

    def get_url(self) -> str:
        url = super().get_url()
        return "/".join([url, self.supply_id])


class CreateSupplyAPIAction(WBAPIAction):
    name = "Создать новую поставку"
    help_text = "Отсутствует"

    path = "supplies"
    method = "POST"

    data_field = "id"

    def __init__(self, api_connector, name: str, page: int = 1, per_page: int = 100):
        super().__init__(api_connector, page=page, per_page=per_page)
        self._body_name = name

    def get_body(self) -> dict:
        return {"name": self._body_name}


class OrdersToSupplyAPIAction(WBAPIAction):
    name = "Добавить к поставке сборочное задание"
    help_text = "Добавляет к поставке сборочное задание и переводит его в статус confirm ('На сборке')"

    path = "supplies/{supply_id}/orders/{order_id}"
    method = "PATCH"

    def __init__(self, api_connector, supply_id: str, order_id: int, page: int = 1, per_page: int = 100):
        super().__init__(api_connector, page=page, per_page=per_page)
        self.supply_id = supply_id
        self.order_id = order_id

    def get_url(self) -> str:
        query_map = {"supply_id": self.supply_id, "order_id": self.order_id}
        return super().get_url().format(**query_map)
