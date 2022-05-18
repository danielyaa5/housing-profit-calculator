from typing import Union, Callable

from src.decimal.dollar import Dollar
from src.decimal.percent import Percent
from src.decimal.rate import Rate


class Purchase(object):
    def __init__(
            self,
            price: Dollar,
            down_payment: Dollar,
            closing_cost_rate,
    ):
        self.price = price
        self.down_payment = down_payment
        self.down_payment_percent = Percent(self.down_payment / self.price * 100)
        self.closing_cost_rate = closing_cost_rate
        self.closing_cost = Dollar(self.price * self.closing_cost_rate)
        self.cost_initial = self.down_payment + self.closing_cost


PurchaseFactoryType = Callable[[], Purchase]


def purchase(
        price: float,
        down_payment: Union[float, None],
        down_payment_percent: Union[float, None],
        closing_cost_percent: float,
) -> PurchaseFactoryType:
    assert down_payment is None or down_payment_percent is None, "down_payment and down_payment_percent are mutually exclusive"
    assert down_payment or down_payment_percent, "down_payment or down_payment_percent is required"

    def factory() -> Purchase:
        return Purchase(
            price=Dollar(price),
            down_payment=Dollar(down_payment or (price * down_payment_percent / 100)),
            closing_cost_rate=Rate(percent=closing_cost_percent or 0),
        )

    return factory
