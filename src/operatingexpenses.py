from typing import Union, Callable

import src.constants as c
from src.decimal.dollar import Dollar
from src.decimal.dollarcompounding import DollarCompYearly
from src.decimal.rate import Rate
from src.income import Income
from src.purchase import Purchase
from src.taxes import Taxes


class OperatingExpenses(object):
    def __init__(
            self,
            purchase: Purchase,
            income: Income,
            taxes: Taxes,
            hoi_rate: Rate,
            hoi_annual_increase_rate: Rate,
            hoa: Dollar,
            hoa_annual_increase_rate: Rate,
            maintenance_rate: Rate,
            maintenance_annual_increase_rate: Rate,
            other_rate: Rate,
            other_annual_increase_rate: Rate,
    ):
        self._income = income

        self.property_tax = taxes.property_tax
        self.property_tax_rate = taxes.property_tax_rate

        hoi_initial = hoi_rate * purchase.price / c.MONTHS_PER_YEAR
        self.hoi_rate = hoi_rate
        self.hoi_annual_increase_rate = hoi_annual_increase_rate
        self.hoi = DollarCompYearly(v0=hoi_initial, rate=self.hoi_annual_increase_rate)

        self.hoa_annual_increase_rate = hoa_annual_increase_rate
        self.hoa = DollarCompYearly(v0=hoa, rate=self.hoa_annual_increase_rate)

        maintenance_initial = maintenance_rate * purchase.price / c.MONTHS_PER_YEAR
        self.maintenance_rate = maintenance_rate
        self.maintenance_annual_increase_rate = maintenance_annual_increase_rate
        self.maintenance = DollarCompYearly(v0=maintenance_initial, rate=self.maintenance_annual_increase_rate)

        other_initial = other_rate * purchase.price / c.MONTHS_PER_YEAR
        self.other_rate = other_rate
        self.other_annual_increase_rate = other_annual_increase_rate
        self.other = DollarCompYearly(v0=other_initial, rate=self.other_annual_increase_rate)

    def vacancy(self, month):
        return Dollar(self._income.vacancy_rate * self._income.tenant_rent[month])

    def management_fee(self, month):
        return Dollar(self._income.management_fee_rate * self._income.rent[month])


OperatingExpensesFactoryType = Callable[[Purchase, Income, Taxes], OperatingExpenses]


def operating_expenses(
        hoi_percent: float,
        hoi_annual_increase_percent: Union[float, None],
        hoa: Union[float, None],
        hoa_annual_increase_percent: Union[float, None],
        maintenance_percent: Union[float, None],
        maintenance_annual_increase_percent: Union[float, None],
        other_percent: Union[float, None],
        other_annual_increase_percent: Union[float, None],
) -> OperatingExpensesFactoryType:
    def factory(purchase: Purchase, income: Income, taxes: Taxes) -> OperatingExpenses:
        return OperatingExpenses(
            purchase=purchase,
            income=income,
            taxes=taxes,
            hoi_rate=Rate(percent=hoi_percent),
            hoi_annual_increase_rate=Rate(percent=hoi_annual_increase_percent or 0),
            hoa=Dollar(hoa or 0),
            hoa_annual_increase_rate=Rate(percent=hoa_annual_increase_percent or 0),
            maintenance_rate=Rate(percent=maintenance_percent or 0),
            maintenance_annual_increase_rate=Rate(percent=maintenance_annual_increase_percent or 0),
            other_rate=Rate(percent=other_percent or 0),
            other_annual_increase_rate=Rate(percent=other_annual_increase_percent or 0),
        )

    return factory
