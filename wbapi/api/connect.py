import asyncio
from typing import List, Iterable

from loguru import logger

from api.enums import SupplyStatus
from api.marketplace import NewOrdersAPIAction, OrdersStatusesAPIAction, CreateSupplyAPIAction, OrdersToSupplyAPIAction
from common.utils import retry


class WBAPIConnector:

    def __init__(self, api_key: str, scopes: List[str], introspect: bool = True, debug: bool = True) -> None:
        self.api_key = api_key
        self.scopes = scopes
        self.introspect = introspect
        self.debug = debug

    def __validate(self) -> None:
        return None

    def get_new_orders(self) -> list:
        new_orders_api_action = NewOrdersAPIAction(self.api_key, self.scopes)
        return new_orders_api_action.do()

    def get_orders_statuses(self, orders_ids: Iterable[int]) -> List[dict]:
        orders_statuses_body = {"orders": orders_ids}
        orders_statuses_api_action = OrdersStatusesAPIAction(self.api_key, self.scopes, body=orders_statuses_body)
        return orders_statuses_api_action.do()

    def create_supply(self, supply_name: str) -> dict:
        create_supply_api_action = CreateSupplyAPIAction(name=supply_name)
        return create_supply_api_action.do()

    def put_orders_into_supply(
        self, supply_id: str, orders: iter
    ) -> None:
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
                self.api_key, self.scopes, supply_id=supply_id, order_id=order_id
            )
            task = asyncio.create_task(async_wb_api_action.async_do())
            tasks.append(task)

        await asyncio.gather(*tasks)
