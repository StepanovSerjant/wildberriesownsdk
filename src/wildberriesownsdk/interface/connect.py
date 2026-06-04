import asyncio
import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from loguru import logger

from wildberriesownsdk.api.actions import (
    CreateSupplyAPIAction,
    GetProductsWithPricesAction,
    GetProductsWithPricesByArticlesAction,
    GetSupplyAPIAction,
    ImageToArticleUploadAction,
    NewOrdersAPIAction,
    OrdersAPIAction,
    OrdersStatusesAPIAction,
    OrdersToSupplyAPIAction,
    UploadPricesAndDiscountsAPIAction,
)
from wildberriesownsdk.api.actions.base import WBAPIAction
from wildberriesownsdk.api.enums import SupplyStatus
from wildberriesownsdk.api.exceptions import WBAPIForbiddenException
from wildberriesownsdk.core.helpers import async_wait


class WBAPIConnector:
    def __init__(
        self,
        api_key: str,
        echo: bool = False,
        convert_to_snake_case: bool = False,
    ) -> None:
        self.api_key = api_key
        self.available_scopes = []
        self.echo = echo
        self.convert_to_snake_case = convert_to_snake_case

    def update_prices_and_discounts(
        self, goods: Sequence[Dict[str, Union[int, float]]]
    ):
        update_prices_and_discounts_api_action = (
            UploadPricesAndDiscountsAPIAction(api_connector=self, goods=goods)
        )
        self._check_action_scope(action=update_prices_and_discounts_api_action)
        return update_prices_and_discounts_api_action.do(
            echo=self.echo, convert_to_snake_case=self.convert_to_snake_case
        )

    def get_new_orders(self) -> list:
        new_orders_api_action = NewOrdersAPIAction(api_connector=self)
        self._check_action_scope(action=new_orders_api_action)
        return new_orders_api_action.do(
            echo=self.echo, convert_to_snake_case=self.convert_to_snake_case
        )

    def get_orders(
        self,
        page: int = 1,
        per_page: int = 100,
        date_from: Optional[datetime.datetime] = None,
        date_to: Optional[datetime.datetime] = None,
    ):
        orders_api_action = OrdersAPIAction(
            api_connector=self,
            page=page,
            per_page=per_page,
            date_from=date_from,
            date_to=date_to,
        )
        self._check_action_scope(action=orders_api_action)
        return orders_api_action.do(
            echo=self.echo, convert_to_snake_case=self.convert_to_snake_case
        )

    def get_orders_statuses(self, orders_ids: Iterable[int]) -> List[dict]:
        orders_statuses_body = {"orders": orders_ids}
        orders_statuses_api_action = OrdersStatusesAPIAction(
            api_connector=self, body=orders_statuses_body
        )
        self._check_action_scope(action=orders_statuses_api_action)
        return orders_statuses_api_action.do(
            echo=self.echo, convert_to_snake_case=self.convert_to_snake_case
        )

    def get_products_with_prices(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> dict:
        products_with_prices_api_action = GetProductsWithPricesAction(
            api_connector=self,
            limit=limit,
            offset=offset,
        )
        self._check_action_scope(action=products_with_prices_api_action)
        return products_with_prices_api_action.do(
            echo=self.echo, convert_to_snake_case=self.convert_to_snake_case
        )

    def get_products_with_prices_by_articles(self, nm_ids: List[int]) -> dict:
        products_with_prices_by_articles_api_action = (
            GetProductsWithPricesByArticlesAction(
                api_connector=self,
                nm_ids=nm_ids,
            )
        )
        self._check_action_scope(
            action=products_with_prices_by_articles_api_action
        )
        return products_with_prices_by_articles_api_action.do(
            echo=self.echo, convert_to_snake_case=self.convert_to_snake_case
        )

    def get_supply_info(self, supply_id: str) -> dict:
        get_supply_info_api_action = GetSupplyAPIAction(
            api_connector=self, supply_id=supply_id
        )
        self._check_action_scope(action=get_supply_info_api_action)
        return get_supply_info_api_action.do(
            echo=self.echo, convert_to_snake_case=self.convert_to_snake_case
        )

    def create_supply(self, supply_name: str) -> dict:
        create_supply_api_action = CreateSupplyAPIAction(
            api_connector=self, name=supply_name
        )
        self._check_action_scope(action=create_supply_api_action)
        return create_supply_api_action.do(
            echo=self.echo, convert_to_snake_case=self.convert_to_snake_case
        )

    def put_orders_into_supply(
        self, supply_id: str, orders: Iterable[Dict[str, Any]]
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

    def create_upload_image_to_article_action(
        self, article: str, file: Path, image_number: int
    ):
        return ImageToArticleUploadAction(
            api_connector=self,
            article=article,
            image_number=image_number,
            file=file,
        )

    def upload_image_to_article(
        self, article: str, file: Union[str, Path], image_number: int
    ):
        file = Path(file) if isinstance(file, str) else file
        action = self.create_upload_image_to_article_action(
            article, file, image_number
        )
        return action.do(
            echo=self.echo, convert_to_snake_case=self.convert_to_snake_case
        )

    def is_all_orders_on_confirm(self, orders_ids: Iterable[int]) -> bool:
        orders_with_updated_statuses = self.get_orders_statuses(orders_ids)
        return all(
            [
                order["supplier_status"] == SupplyStatus.CONFIRM.value
                for order in orders_with_updated_statuses
            ]
        )

    async def async_put_orders_to_supply(
        self, supply_id: str, orders: Iterable[Dict[str, Any]]
    ):
        results = []
        for order in orders:
            async_wb_api_action = OrdersToSupplyAPIAction(
                api_connector=self, supply_id=supply_id, order_id=order["id"]
            )
            task = asyncio.create_task(
                async_wb_api_action.async_do(
                    echo=self.echo,
                    convert_to_snake_case=self.convert_to_snake_case,
                )
            )
            tasks = [task, async_wait(0.8)]

            order_result, _ = await asyncio.gather(*tasks)
            results.append(order_result)

        return results

    def _check_action_scope(self, action: WBAPIAction) -> None:
        if action.api_scope not in self.available_scopes:
            available_scopes_str = ", ".join(self.available_scopes)
            raise WBAPIForbiddenException(
                f"Ваш токен соответствует категориям: {available_scopes_str}\nОтсутствует необходимая категория {action.api_scope}"
            )
