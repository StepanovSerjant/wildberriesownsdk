import enum


@enum.unique
class SupplyStatus(enum.Enum):
    CONFIRM = "confirm"
    NEW = "new"
    COMPLETE = "complete"
    CANCEL = "cancel"


@enum.unique
class WBStatus(enum.Enum):
    WAITING = "waiting"  # сборочное задание в работе
    SORTED = "sorted"  # сборочное задание отсортировано
    SOLD = "sold"  # сборочное задание получено покупателем
    CANCELED = "canceled"  # отмена сборочного задания
    CANCELED_BY_CLIENT = (
        "canceled_by_client"  # покупатель отменил заказ при получении
    )
    DECLINED_BY_CLIENT = (
        "declined_by_client"  # покупатель отменил заказ в первый чаc new
    )
    DEFECT = "defect"  # отмена сборочного задания по причине брака
    READY_FOR_PICKUP = "ready_for_pickup"  # сборочное задание прибыло на ПВЗ
