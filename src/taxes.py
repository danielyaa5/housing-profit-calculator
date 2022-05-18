from typing import Callable

import src.constants as c
from src.decimal.dollar import Dollar
from src.decimal.dollarcompounding import DollarCompYearly
from src.decimal.rate import Rate
from src.helpers import rel, yaml_safe_load
from src.mortgage import Mortgage
from src.purchase import Purchase

STATE_TAXES = yaml_safe_load(rel('../taxes/state/ca.yaml'))
FEDERAL_TAXES = yaml_safe_load(rel('../taxes/federal.yaml'))
MAX_DEDUCTIBLE_PROPERTY_TAX = Dollar(FEDERAL_TAXES['property_tax_limit'])


class Taxes(object):
    def __init__(
            self,
            mortgage: Mortgage,
            purchase: Purchase,
            property_tax_rate: Rate,
            property_tax_annual_increase_rate: Rate,
            federal_tax_rate: Rate,
            state_tax_rate: Rate,
            yearly_income: Dollar,
    ):
        property_tax_initial = property_tax_rate * purchase.price / c.MONTHS_PER_YEAR
        self.property_tax_rate = property_tax_rate
        self.property_tax_annual_increase_rate = property_tax_annual_increase_rate
        self.property_tax = DollarCompYearly(v0=property_tax_initial, rate=self.property_tax_annual_increase_rate)
        self.federal_tax_rate = federal_tax_rate
        self.state_tax_rate = state_tax_rate
        self.yearly_income = yearly_income
        self.federal_standard_deduction = Dollar(FEDERAL_TAXES['standard_deduction'])
        self.state_standard_deduction = Dollar(STATE_TAXES['standard_deduction'])
        self.tax_deduction_per_year = self._calculate_tax_deduction_per_year(mortgage)

    def _calculate_tax_deduction_per_year(self, mortgage: Mortgage):
        tax_deduction_per_year = [0]
        for year_num, principle, interest, deductible_interest in mortgage.yearly_mortgage_schedule():
            deductible_property_tax = min(self.property_tax[0], MAX_DEDUCTIBLE_PROPERTY_TAX)
            theoretical_deduction = deductible_property_tax + deductible_interest
            tax_deduction_per_year.append(min(theoretical_deduction, self.yearly_income))

        return tax_deduction_per_year


TaxesFactoryType = Callable[[Mortgage, Purchase], Taxes]


def taxes(
        property_tax_percent: float,
        property_tax_annual_increase_percent: float,
        federal_tax_rate_percent: float,
        state_tax_rate_percent: float,
        yearly_income: float,
) -> TaxesFactoryType:
    def factory(mortgage: Mortgage, purchase: Purchase):
        return Taxes(
            mortgage=mortgage,
            purchase=purchase,
            property_tax_rate=Rate(percent=property_tax_percent),
            property_tax_annual_increase_rate=Rate(percent=property_tax_annual_increase_percent or 0),
            federal_tax_rate=Rate(percent=federal_tax_rate_percent),
            state_tax_rate=Rate(percent=state_tax_rate_percent),
            yearly_income=Dollar(yearly_income),
        )

    return factory
