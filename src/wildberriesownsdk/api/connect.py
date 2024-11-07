import asyncio
from typing import Iterable, List

from loguru import logger

from wildberriesownsdk.api.enums import SupplyStatus
from wildberriesownsdk.api.introspect import (
    IntrospectAPIKeyAPIAction,
    WBIntrospectAPIKeySummary,
)
from wildberriesownsdk.api.marketplace import (
    CreateSupplyAPIAction,
    NewOrdersAPIAction,
    OrdersStatusesAPIAction,
    OrdersToSupplyAPIAction,
)
from wildberriesownsdk.common.exceptions import APIKeyIntrospectionException
from wildberriesownsdk.common.utils import retry


class WBAPIConnector:

    def __init__(
        self,
        api_key: str,
        scopes: List[str],
        introspect: bool = True,
        debug: bool = True,
    ) -> None:
        self.api_key = api_key
        self.scopes = scopes
        self.introspect = introspect
        self.debug = debug

    def get_new_orders(self) -> list:
        new_orders_api_action = NewOrdersAPIAction(api_connector=self)
        return new_orders_api_action.do()

    def get_orders_statuses(self, orders_ids: Iterable[int]) -> List[dict]:
        orders_statuses_body = {"orders": orders_ids}
        orders_statuses_api_action = OrdersStatusesAPIAction(
            api_connector=self, body=orders_statuses_body
        )
        return orders_statuses_api_action.do()

    def create_supply(self, supply_name: str) -> dict:
        create_supply_api_action = CreateSupplyAPIAction(
            api_connector=self, name=supply_name
        )
        return create_supply_api_action.do()

    def perform_introspect(self) -> WBIntrospectAPIKeySummary:
        introspect_api_action = IntrospectAPIKeyAPIAction(api_connector=self)
        response = introspect_api_action.do()

        token_summary = response.get("summary", {})
        if not token_summary:
            raise APIKeyIntrospectionException(
                "Не удалось получить информацию о токене."
            )

        summary_fields_to_exclude = (
            "token_id",
            "x_supplier_id",
        )
        for field in summary_fields_to_exclude:
            token_summary.pop(field, None)

        introspect_summary = WBIntrospectAPIKeySummary(**token_summary)
        if not all(
            [scope in introspect_summary.scopes_decoded for scope in self.scopes]
        ):
            raise APIKeyIntrospectionException(
                "Ваш API токен не обладает определенными правами для действий скрипта."
            )

        return introspect_summary

    def put_orders_into_supply(self, supply_id: str, orders: iter) -> None:
        asyncio.run(self.async_put_orders_to_supply(supply_id, orders))

        orders_ids = [order["id"] for order in orders]
        is_success = self.is_all_orders_on_confirm(orders_ids)
        if is_success:
            logger.info(f"Поставка - {supply_id} успешно собрана\n")
        else:
            logger.error(
                f"Не удалось подтвердить статус заказов внутри поставки - {supply_id}"
            )

    @retry(target_value=True, tries=3)
    def is_all_orders_on_confirm(self, orders_ids: iter) -> bool:
        orders_with_updated_statuses = self.get_orders_statuses(orders_ids)
        return all(
            [
                order["supplier_status"] == SupplyStatus.CONFIRM.value
                for order in orders_with_updated_statuses
            ]
        )

    async def async_put_orders_to_supply(self, supply_id: str, orders: Iterable[dict]):
        tasks = []
        for order in orders:
            order_id = order["id"]
            async_wb_api_action = OrdersToSupplyAPIAction(
                api_connector=self, supply_id=supply_id, order_id=order_id
            )
            task = asyncio.create_task(async_wb_api_action.async_do())
            tasks.append(task)

        await asyncio.gather(*tasks)
