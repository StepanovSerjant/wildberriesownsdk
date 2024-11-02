import datetime
from typing import List

from base import WBAPIAction


class OrdersAPIAction(WBAPIAction):
    name = "Получить информацию по сборочным заданиям"
    help_text = (
        "Возвращает информацию по сборочным заданиям без их актуального статуса."
        "Можно выгрузить данные за конкретный период, максимум 30 календарных дней"
    )

    path = "orders"
    method = "GET"
    paginated = True

    data_field = "orders"

    def __init__(self, api_key: str, api_scopes: List[str], by_datetime: datetime.datetime, period_days: int = 3, page: int = 1):
        super().__init__(api_key=api_key, api_scopes=api_scopes, page=page)
        self.by_datetime = by_datetime
        self.period_days = period_days

    def get_query_params(self):
        query_params = super().get_query_params()
        query_params.update(**self._create_date_from_and_date_to_query_params())
        return query_params

    def _create_date_from_and_date_to_query_params(self) -> dict:
        min_dtm = datetime.datetime.combine(
            self.by_datetime - datetime.timedelta(days=self.period_days),
            datetime.datetime.min.time(),
        )
        return {
            "dateFrom": int(
                datetime.datetime.strftime(
                    min_dtm,
                    "%s",
                )
            ),
            "dateTo": int(
                datetime.datetime.strftime(
                    self.by_datetime,
                    "%s",
                )
            ),
        }


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

    def __init__(self, api_key: str, api_scopes: List[str], body: dict, page: int = 1):
        super().__init__(api_key=api_key, api_scopes=api_scopes, page=page)
        self._request_body = body

    def get_body(self) -> dict:
        return self._request_body


class CreateSupplyAPIAction(WBAPIAction):
    name = "Создать новую поставку"
    help_text = "Отсутствует"

    path = "supplies"
    method = "POST"

    data_field = "id"

    def __init__(self, api_key: str, api_scopes: List[str], name: str, page: int = 1):
        super().__init__(api_key=api_key, api_scopes=api_scopes, page=page)
        self._body_name = name

    def get_body(self) -> dict:
        return {"name": self._body_name}


class OrdersToSupplyAPIAction(WBAPIAction):
    name = "Добавить к поставке сборочное задание"
    help_text = "Добавляет к поставке сборочное задание и переводит его в статус confirm ('На сборке')"

    path = "supplies/{supply_id}/orders/{order_id}"
    method = "PATCH"

    def __init__(self, api_key: str, api_scopes: List[str], supply_id: str, order_id: int, page: int = 1):
        super().__init__(api_key=api_key, api_scopes=api_scopes, page=page)
        self.supply_id = supply_id
        self.order_id = order_id

    def get_url(self) -> str:
        query_map = {"supply_id": self.supply_id, "order_id": self.order_id}
        return super().get_url().format(**query_map)
