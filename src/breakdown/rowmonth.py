from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import src.constants as c
from src.breakdown.row import BreakdownRow
from src.decimal.dollar import Dollar
from src.decimal.percent import Percent
from src.helpers import compound_interest

if TYPE_CHECKING:
    from src.homeinvestment import HomeInvestment


class RowMonth(BreakdownRow):
    def __init__(
            self,
            home_investment: HomeInvestment,
            month,
            year,
            principle,
            interest,
            deductible_interest,
            net_operating_cost,
            net_income,
            net_cashflow,
            principle_paid,
            interest_paid,
            appreciated_price,
            index_fund_value,
            cashflow_surplus_index_fund_value,
    ):
        # Private
        purchase = home_investment.purchase
        taxes = home_investment.taxes
        operating_expenses = home_investment.operating_expenses
        income = home_investment.income
        sale = home_investment.sale
        self._home_investment = home_investment

        # Time
        self.year = year
        self.month = month

        # Cashflow Negative
        self.monthly_principle = principle
        self.monthly_interest = interest
        self.monthly_mortgage = principle + interest
        self.monthly_property_tax = taxes.property_tax[month]
        self.monthly_hoi = operating_expenses.hoi[month]
        self.monthly_hoa = operating_expenses.hoa[month]
        self.monthly_vacancy = operating_expenses.vacancy(month=month)
        self.monthly_maintenance = operating_expenses.maintenance[month]
        self.monthly_management_fee = operating_expenses.management_fee(month=month)
        self.monthly_operating_cost = sum([
            self.monthly_property_tax,
            self.monthly_hoi,
            self.monthly_hoa,
            self.monthly_vacancy,
            self.monthly_maintenance,
            self.monthly_management_fee,
        ])
        self.net_operating_cost = self.monthly_operating_cost + net_operating_cost
        self.monthly_expenses = sum([
            self.monthly_property_tax,
            self.monthly_hoi,
            self.monthly_hoa,
            self.monthly_maintenance,
        ])

        # Cashflow Positive
        self.monthly_deductible_interest = deductible_interest
        self.monthly_tax_savings = income.tax_savings_per_month[month]
        self.monthly_rent = income.rent[month]
        self.monthly_tenant_rent = income.tenant_rent[month]
        self.monthly_income = self.monthly_tax_savings + self.monthly_rent + self.monthly_tenant_rent
        self.monthly_adjusted_income = self.monthly_income - self.monthly_vacancy - self.monthly_management_fee

        # Cashflow
        self.net_income = net_income + self.monthly_income
        if month == 0:
            self.monthly_cashflow = -(purchase.down_payment + purchase.closing_cost)
        else:
            self.monthly_cashflow = self.monthly_income - self.monthly_operating_cost - self.monthly_mortgage
        self.net_cashflow = net_cashflow + self.monthly_cashflow

        # Home Investment Value
        self.appreciated_price = purchase.price if month == 0 else appreciated_price
        self.monthly_appreciation = sale.appreciation_per_month(year=year)
        self.appreciated_price = self.appreciated_price + self.monthly_appreciation
        self.appreciation = self.appreciated_price - purchase.price
        self.principle_paid = principle_paid + principle
        self.interest_paid = interest_paid + interest
        self.sale_closing_cost = self.appreciated_price * sale.closing_cost_rate
        self.equity = self.appreciation + self.principle_paid + purchase.down_payment
        self.cashflow_surplus_index_fund_value = cashflow_surplus_index_fund_value
        if month != 0:
            self.cashflow_surplus_index_fund_value = compound_interest(
                principle=self.cashflow_surplus_index_fund_value,
                rate=home_investment.index_fund_annual_return_rate,
                years=Decimal(1 / c.MONTHS_PER_YEAR),
                number=Decimal(c.MONTHS_PER_YEAR)
            )

        if self.monthly_cashflow > 0:
            self.cashflow_surplus_index_fund_value += self.monthly_cashflow

        self.cash_to_receive = self.equity - self.sale_closing_cost
        self.home_investment_value = self.cash_to_receive + self.cashflow_surplus_index_fund_value - self.net_operating_cost - self.interest_paid

        # Index Fund Value
        self.index_fund_value = index_fund_value
        if month != 0:
            self.index_fund_value = compound_interest(
                principle=self.index_fund_value,
                rate=home_investment.index_fund_annual_return_rate,
                years=Decimal(1 / c.MONTHS_PER_YEAR),
                number=Decimal(c.MONTHS_PER_YEAR)
            )

        if self.monthly_cashflow < 0:
            self.index_fund_value += abs(self.monthly_cashflow)

        # Home Investment vs Index Fund ROI Comparison
        self.home_roi = Percent(self.home_investment_value / purchase.cost_initial * 100 - 100)
        self.index_fund_roi = Percent(self.index_fund_value / purchase.cost_initial * 100 - 100)
        self.score = Percent(self.home_investment_value / self.index_fund_value * 100 - 100)

    def is_last_month(self):
        return self._home_investment.mortgage.loan_term_months == self.month

    def is_full_year(self):
        return self.month % c.MONTHS_PER_YEAR == 0

    def is_new_year(self):
        return self.month % c.MONTHS_PER_YEAR == 1
