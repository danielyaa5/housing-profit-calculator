from typing import Union, Callable

import src.constants as c
from src.decimal.dollar import Dollar
from src.decimal.dollarcompounding import DollarCompYearly
from src.decimal.rate import Rate
from src.taxes import Taxes


class Income(object):
    def __init__(
            self,
            taxes: Taxes,
            rent: Dollar,
            rent_annual_increase_rate: Rate,
            tenant_rent: Dollar,
            tenant_rent_annual_increase_rate: Rate,
            vacancy_rate: Rate,
            management_fee_rate: Rate,
    ):
        self.rent_annual_increase_rate = rent_annual_increase_rate
        self.rent = DollarCompYearly(v0=rent, rate=self.rent_annual_increase_rate)
        self.tenant_rent_annual_increase_rate = tenant_rent_annual_increase_rate
        self.tenant_rent = DollarCompYearly(v0=tenant_rent, rate=self.tenant_rent_annual_increase_rate)
        self.vacancy_rate = vacancy_rate
        self.management_fee_rate = management_fee_rate
        self.tax_savings_per_month, self.tax_savings_per_year = self._calculate_tax_savings(taxes)

    @staticmethod
    def _calculate_tax_savings(taxes: Taxes):
        tax_savings_per_year = [Dollar(0)]
        tax_savings_per_month = [Dollar(0)]
        for year, tax_deduction in enumerate(taxes.tax_deduction_per_year):
            if year == 0:
                continue
            federal_itemized_savings = Dollar(taxes.federal_tax_rate * tax_deduction)
            federal_standard_deduction_savings = Dollar(taxes.federal_tax_rate * taxes.federal_standard_deduction)
            federal_savings = max(federal_itemized_savings - federal_standard_deduction_savings, Dollar(0))

            state_itemized_savings = Dollar(taxes.state_tax_rate * tax_deduction)
            state_standard_deduction_savings = Dollar(taxes.state_tax_rate * taxes.state_standard_deduction)
            state_savings = max(state_itemized_savings - state_standard_deduction_savings, Dollar(0))

            total_savings = federal_savings + state_savings
            tax_savings_per_year.append(total_savings)
            for i in range(c.MONTHS_PER_YEAR):
                tax_savings_per_month.append(total_savings / c.MONTHS_PER_YEAR)

        return tax_savings_per_month, tax_savings_per_year


IncomeFactoryType = Callable[[Taxes], Income]


def income(
        rent: Union[float, None],
        rent_annual_increase_percent: Union[float, None],
        tenant_rent: Union[float, None],
        tenant_rent_annual_increase_percent: Union[float, None],
        vacancy_percent: Union[float, None],
        management_fee_percent: Union[float, None],
) -> IncomeFactoryType:
    return lambda taxes: Income(
            taxes=taxes,
            rent=Dollar(rent or 0),
            rent_annual_increase_rate=Rate(percent=rent_annual_increase_percent or 0),
            tenant_rent=Dollar(tenant_rent or 0),
            tenant_rent_annual_increase_rate=Rate(percent=tenant_rent_annual_increase_percent or 0),
            vacancy_rate=Rate(percent=vacancy_percent or 0),
            management_fee_rate=Rate(percent=management_fee_percent or 0),
        )

