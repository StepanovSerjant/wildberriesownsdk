from dataclasses import dataclass, asdict
from http import HTTPMethod
from typing import Dict, Union, Sequence, Optional, List

from wildberriesownsdk.api.actions.base import WBAPIAction


@dataclass(frozen=True)
class PriceAndDiscountOfGoodSchema:
    nm_id: int
    price: int
    discount: int

    def to_dict(self):
        dict_instance = asdict(self)
        dict_instance["nmID"] = dict_instance.pop("nm_id")
        return dict_instance


class PriceAndDiscountsAPIDetailsMixin:
    api_url = "https://discounts-prices-api.wildberries.ru/apii"
    api_version = "v2"


class UploadPricesAndDiscountsAPIAction(PriceAndDiscountsAPIDetailsMixin, WBAPIAction):
    name = "Установить цены и скидки для товаров"

    path = "upload/task"
    method = HTTPMethod.POST

    def __init__(self, api_connector, goods: Sequence[Dict[str, Union[int, float]]], page: int = 1, per_page: int = 100):
        super().__init__(api_connector, page=page, per_page=per_page)
        self.goods = goods

    def get_body(self):
        serialized_goods = [PriceAndDiscountOfGoodSchema(**good).to_dict() for good in self.goods]
        return {"data": serialized_goods}


class GetProductsWithPricesAction(PriceAndDiscountsAPIDetailsMixin, WBAPIAction):
    """
    https://dev.wildberries.ru/en/openapi/work-with-products/#tag/Prices-and-Discounts/paths/~1api~1v2~1list~1goods~1filter/get
    """
    name = "Получить товары с ценами"

    path = "list/goods/filter"
    method = HTTPMethod.GET

    root_data_field = "data"

    def __init__(self, api_connector, limit: Optional[int] = None, offset: Optional[int] = None, page: int = 1, per_page: int = 100):
        super().__init__(api_connector, page=page, per_page=per_page)
        self.limit = limit
        self.offset = offset

    def get_query_params(self):
        query_params = {}
        if self.limit:
            query_params.update(limit=self.limit)

        if self.offset:
            query_params.update(offset=self.offset)

        return query_params


class GetProductsWithPricesByArticlesAction(PriceAndDiscountsAPIDetailsMixin, WBAPIAction):
    """
    https://dev.wildberries.ru/en/openapi/work-with-products/#tag/Prices-and-Discounts/paths/~1api~1v2~1list~1goods~1filter/post
    """
    name = "Получить товары с ценами по списку артикулов"

    path = "list/goods/filter"
    method = HTTPMethod.POST

    root_data_field = "data"

    def __init__(self, api_connector, nm_ids: List[int], page: int = 1, per_page: int = 100):
        super().__init__(api_connector, page=page, per_page=per_page)
        self.nm_ids = nm_ids

    def get_body(self):
        return {"nmList": self.nm_ids}
