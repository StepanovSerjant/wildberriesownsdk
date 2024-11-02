import enum


@enum.unique
class SupplyStatus(enum.Enum):
    CONFIRM: str = "confirm"
    NEW: str = "new"
    COMPLETE: str = "complete"
    CANCEL: str = "cancel"


@enum.unique
class WBStatus(enum.Enum):
    WAITING: str = "waiting"  # сборочное задание в работе
    SORTED: str = "sorted"  # сборочное задание отсортировано
    SOLD: str = "sold"  # сборочное задание получено покупателем
    CANCELED: str = "canceled"  # отмена сборочного задания
    CANCELED_BY_CLIENT: str = (
        "canceled_by_client"  # покупатель отменил заказ при получении
    )
    DECLINED_BY_CLIENT: str = (
        "declined_by_client"  # покупатель отменил заказ в первый чаc new
    )
    DEFECT: str = "defect"  # отмена сборочного задания по причине брака
    READY_FOR_PICKUP: str = "ready_for_pickup"  # сборочное задание прибыло на ПВЗ
