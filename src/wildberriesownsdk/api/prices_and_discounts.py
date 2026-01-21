from dataclasses import dataclass, asdict
from typing import Dict, Union, Sequence, Optional, List

from wildberriesownsdk.api.base import WBAPIAction
from wildberriesownsdk.common import config


@dataclass(frozen=True)
class PriceAndDiscountOfGoodSchema:
    nm_id: int
    price: int
    discount: int

    def to_dict(self):
        dict_instance = asdict(self)
        dict_instance["nmID"] = dict_instance.pop("nm_id")
        return dict_instance


class UploadPricesAndDiscountsAPIAction(WBAPIAction):
    name = "Установить цены и скидки для товаров"
    help_text = "Отсутствует"

    path = "upload/task"
    method = "POST"

    def __init__(self, api_connector, goods: Sequence[Dict[str, Union[int, float]]], page: int = 1, per_page: int = 100):
        super().__init__(api_connector, page=page, per_page=per_page)
        self.goods = goods

    def get_url(self) -> str:
        return f"{config.BASE_PRICES_AND_DISCOUNTS_API_URL}/{config.PRICES_AND_DISCOUNTS_API_VERSION}/{self.path}"

    def get_body(self) -> dict:
        serialized_goods = [PriceAndDiscountOfGoodSchema(**good).to_dict() for good in self.goods]
        return {"data": serialized_goods}


class GetProductsWithPricesAction(WBAPIAction):
    """
    https://dev.wildberries.ru/en/openapi/work-with-products/#tag/Prices-and-Discounts/paths/~1api~1v2~1list~1goods~1filter/get
    """
    name = "Получить товары с ценами"
    help_text = "Отсутствует"

    path = "list/goods/filter"
    method = "GET"

    data_field = "data"

    def __init__(self, api_connector, limit: Optional[int] = None, offset: Optional[int] = None, page: int = 1, per_page: int = 100):
        super().__init__(api_connector, page=page, per_page=per_page)
        self.limit = limit
        self.offset = offset

    def get_url(self) -> str:
        return f"{config.BASE_PRICES_AND_DISCOUNTS_API_URL}/{config.PRICES_AND_DISCOUNTS_API_VERSION}/{self.path}"

    def get_query_params(self) -> dict:
        query_params = {}
        if self.limit:
            query_params.update(limit=self.limit)

        if self.offset:
            query_params.update(offset=self.offset)

        return query_params


class GetProductsWithPricesByArticlesAction(WBAPIAction):
    """
    https://dev.wildberries.ru/en/openapi/work-with-products/#tag/Prices-and-Discounts/paths/~1api~1v2~1list~1goods~1filter/post
    """
    name = "Получить товары с ценами по списку артикулов"
    help_text = "Отсутствует"

    path = "list/goods/filter"
    method = "POST"

    data_field = "data"

    def __init__(self, api_connector, nm_ids: List[int], page: int = 1, per_page: int = 100):
        super().__init__(api_connector, page=page, per_page=per_page)
        self.nm_ids = nm_ids

    def get_url(self) -> str:
        return f"{config.BASE_PRICES_AND_DISCOUNTS_API_URL}/{config.PRICES_AND_DISCOUNTS_API_VERSION}/{self.path}"

    def get_body(self) -> dict:
        return {"nmList": self.nm_ids}
