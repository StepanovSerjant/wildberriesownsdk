import asyncio
import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Dict, Union, Sequence

from loguru import logger

from wildberriesownsdk.api.content import ImageToArticleUploadAction
from wildberriesownsdk.api.enums import SupplyStatus
from wildberriesownsdk.api.introspect import (
    IntrospectAPIKeyAPIAction,
    WBIntrospectAPIKeySummary,
)
from wildberriesownsdk.api.marketplace import (
    CreateSupplyAPIAction,
    GetSupplyAPIAction,
    NewOrdersAPIAction,
    OrdersAPIAction,
    OrdersStatusesAPIAction,
    OrdersToSupplyAPIAction,
)
from wildberriesownsdk.api.prices_and_discounts import UploadPricesAndDiscountsAPIAction
from wildberriesownsdk.common.decorators import request_per_seconds, retry
from wildberriesownsdk.common.exceptions import APIKeyIntrospectionException
from wildberriesownsdk.common.utils import async_wait


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

    def update_prices_and_discounts(self, goods: Sequence[Dict[str, Union[int, float]]]):
        update_prices_and_discounts_api_action = UploadPricesAndDiscountsAPIAction(api_connector=self, goods=goods)
        return update_prices_and_discounts_api_action.do()

    def get_new_orders(self) -> list:
        new_orders_api_action = NewOrdersAPIAction(api_connector=self)
        return new_orders_api_action.do()

    def get_orders(self, page: int = 1, per_page: int = 100, date_from: Optional[datetime.datetime] = None, date_to: Optional[datetime.datetime] = None):
        orders_api_action = OrdersAPIAction(
            api_connector=self,
            page=page,
            per_page=per_page,
            date_from=date_from,
            date_to=date_to,
        )
        return orders_api_action.do()

    @request_per_seconds(seconds=0.8)
    def get_orders_statuses(self, orders_ids: Iterable[int]) -> List[dict]:
        orders_statuses_body = {"orders": orders_ids}
        orders_statuses_api_action = OrdersStatusesAPIAction(
            api_connector=self, body=orders_statuses_body
        )
        return orders_statuses_api_action.do()

    @request_per_seconds(seconds=0.8)
    def get_supply_info(self, supply_id: str) -> dict:
        get_supply_info_api_action = GetSupplyAPIAction(
            api_connector=self, supply_id=supply_id
        )
        return get_supply_info_api_action.do()

    def create_supply(self, supply_name: str) -> dict:
        create_supply_api_action = CreateSupplyAPIAction(
            api_connector=self, name=supply_name
        )
        return create_supply_api_action.do()

    def perform_introspect(self) -> WBIntrospectAPIKeySummary:
        introspect_api_action = IntrospectAPIKeyAPIAction(api_connector=self)
        response = introspect_api_action.do()

        if not response.get("ok", False):
            exception_texts = ["Токен не найден."]
            if public_error_message := response.get("public_error_message"):
                exception_texts.append(public_error_message)

            raise APIKeyIntrospectionException(" ".join(exception_texts))

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

    def create_upload_image_to_article_action(
        self, article: str, file: Path, image_number: int
    ):
        return ImageToArticleUploadAction(
            api_connector=self, article=article, image_number=image_number, file=file
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
        results = []
        for order in orders:
            async_wb_api_action = OrdersToSupplyAPIAction(
                api_connector=self, supply_id=supply_id, order_id=order["id"]
            )
            task = asyncio.create_task(async_wb_api_action.async_do())
            tasks = [task, async_wait(0.8)]

            order_result, _ = await asyncio.gather(*tasks)
            results.append(order_result)

        return results
