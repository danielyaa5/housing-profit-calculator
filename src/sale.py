from typing import Union, Callable

import src.constants as c
from src.decimal.dollar import Dollar
from src.decimal.dollarcompounding import DollarCompYearly
from src.decimal.rate import Rate
from src.purchase import Purchase


class Sale(object):
    def __init__(
            self,
            purchase: Purchase,
            closing_cost_rate: Rate,
            annual_appreciation_rate: Rate,
    ):
        self.closing_cost_rate = closing_cost_rate
        self.annual_appreciation_rate = annual_appreciation_rate
        self.appreciated_price = DollarCompYearly(v0=purchase.price, rate=self.annual_appreciation_rate)

    def appreciation_per_year(self, year):
        if year == 0:
            return Dollar(0)
        return self.appreciated_price.year(num_years=year) - self.appreciated_price.year(num_years=year - 1)

    def appreciation_per_month(self, year):
        return self.appreciation_per_year(year=year) / c.MONTHS_PER_YEAR


SaleFactoryType = Callable[[Purchase], Sale]


def sale(
        closing_cost_percent: float,
        annual_appreciation_percent: Union[float, None],
) -> SaleFactoryType:
    return lambda purchase: Sale(
        purchase=purchase,
        closing_cost_rate=Rate(percent=closing_cost_percent),
        annual_appreciation_rate=Rate(percent=annual_appreciation_percent or 0),
    )
