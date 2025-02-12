from wildberriesownsdk.api.base import WBAPIAction
from wildberriesownsdk.api.enums import WBScope


class NewOrdersAPIAction(WBAPIAction):
    name = "Получить список новых сборочных заданий"
    help_text = (
        "Возвращает список всех новых сборочных заданий у продавца на данный момент"
    )

    method = "GET"
    path = "orders/new"
    scope = WBScope.MARKETPLACE.value

    paginated = True
    data_field = "orders"


class OrdersStatusesAPIAction(WBAPIAction):
    name = "Получить статусы сборочных заданий"
    help_text = (
        "Возвращает статусы сборочных заданий по переданному списку идентификаторов сборочных заданий."
        "supplierStatus - статус сборочного задания, триггером изменения которого является сам продавец."
    )

    method = "POST"
    path = "orders/status"
    scope = WBScope.MARKETPLACE.value

    data_field = "orders"

    def __init__(self, api_connector, body: dict, page: int = 1):
        super().__init__(api_connector, page=page)
        self._request_body = body

    def get_body(self) -> dict:
        return self._request_body


class GetSupplyAPIAction(WBAPIAction):
    name = "Получить информацию о поставке"
    help_text = "Возвращает информацию о поставке."

    method = "GET"
    path = "supplies"
    scope = WBScope.MARKETPLACE.value

    def __init__(self, api_connector, supply_id: str, page: int = 1):
        super().__init__(api_connector, page=page)
        self.supply_id = supply_id

    def get_url(self) -> str:
        url = super().get_url()
        return "/".join([url, self.supply_id])


class CreateSupplyAPIAction(WBAPIAction):
    name = "Создать новую поставку"
    help_text = "Отсутствует"
    scope = WBScope.MARKETPLACE.value

    path = "supplies"
    method = "POST"

    data_field = "id"

    def __init__(self, api_connector, name: str, page: int = 1):
        super().__init__(api_connector, page=page)
        self._body_name = name

    def get_body(self) -> dict:
        return {"name": self._body_name}


class OrdersToSupplyAPIAction(WBAPIAction):
    name = "Добавить к поставке сборочное задание"
    help_text = "Добавляет к поставке сборочное задание и переводит его в статус confirm ('На сборке')"

    method = "PATCH"
    path = "supplies/{supply_id}/orders/{order_id}"
    scope = WBScope.MARKETPLACE.value

    def __init__(self, api_connector, supply_id: str, order_id: int, page: int = 1):
        super().__init__(api_connector=api_connector, page=page)
        self.supply_id = supply_id
        self.order_id = order_id

    def get_url(self) -> str:
        query_map = {"supply_id": self.supply_id, "order_id": self.order_id}
        return super().get_url().format(**query_map)
