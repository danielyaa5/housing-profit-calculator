from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Generator

import constants as c
from decimaldollar import DecimalDollar
from decimalpercent import DecimalPercent
from helpers import compound_interest
from investmentsummary import InvestmentSummary, SummaryRow

if TYPE_CHECKING:
    from homeinvestment import HomeInvestment


class MonthlySummary(InvestmentSummary):
    def __init__(self, home_investment: HomeInvestment, years=None, months=None):
        super().__init__(home_investment)
        self._years = years
        self._months = months

    def generator(self) -> Generator[Month, None, None]:
        mortgage = self._home_investment.mortgage
        last = None

        for month, principle, interest, deductible_interest in mortgage.monthly_mortgage_schedule():
            year = (month - 1) // c.MONTHS_PER_YEAR + 1
            if self._years and year > self._years:
                return

            if self._months and month > self._months:
                return

            last = Month(
                home_investment=self._home_investment,
                month=month,
                year=year,
                principle=principle,
                interest=interest,
                deductible_interest=deductible_interest,
                net_cashflow=last.net_cashflow if last else -self._home_investment.initial_cost,
                net_expenses=last.net_expenses if last else self._home_investment.purchase_closing_cost,
                principle_paid=last.principle_paid if last else DecimalDollar(0),
                appreciated_price=last.appreciated_price if last else self._home_investment.purchase_price,
                index_fund_value=last.index_fund_value if last else self._home_investment.initial_cost,
            )
            yield last

    def csv(self):
        return self._csv('monthly')


class Month(SummaryRow):
    def __init__(
            self,
            home_investment: HomeInvestment,
            month,
            year,
            principle,
            interest,
            deductible_interest,
            net_cashflow,
            net_expenses,
            principle_paid,
            appreciated_price,
            index_fund_value,
    ):
        # Private
        self._home_investment = home_investment

        # Time
        self.year = year
        self.month = month

        # Cashflow Negative
        self.monthly_principle = principle
        self.monthly_interest = interest
        self.monthly_mortgage = principle + interest
        self.monthly_property_tax = home_investment.property_tax
        self.monthly_home_insurance = home_investment.home_insurance
        self.monthly_vacancy_cost = home_investment.vacancy_cost(year)
        self.monthly_expenses = sum([
            interest,
            home_investment.property_tax,
            home_investment.home_insurance,
            home_investment.hoa,
            self.monthly_vacancy_cost
        ])
        self.monthly_cashflow_negative = principle + self.monthly_expenses

        # Cashflow Positive
        self.monthly_deductible_interest = deductible_interest
        self.monthly_state_tax_savings = home_investment.state_tax_savings(year) / c.MONTHS_PER_YEAR
        self.monthly_federal_tax_savings = home_investment.federal_tax_savings(year) / c.MONTHS_PER_YEAR
        self.monthly_tax_savings = self.monthly_federal_tax_savings + self.monthly_state_tax_savings
        self.monthly_rent = home_investment.rent(year)
        self.monthly_tenant_rent = home_investment.tenant_rent(year)
        self.monthly_cashflow_positive = self.monthly_tax_savings + self.monthly_rent + self.monthly_tenant_rent

        # Cashflow
        self.monthly_cashflow = self.monthly_cashflow_positive - self.monthly_cashflow_negative
        self.net_cashflow = net_cashflow + self.monthly_cashflow

        # Home Investment vs Index Fund Comparison
        self.monthly_appreciation = home_investment.monthly_appreciation(year)
        self.appreciated_price = appreciated_price + self.monthly_appreciation
        self.appreciation = self.appreciated_price - home_investment.purchase_price
        self.principle_paid = principle_paid + principle
        self.sale_closing_cost = self.appreciated_price * home_investment.sale_closing_cost_rate
        self.net_expenses = self.monthly_expenses + net_expenses
        self.equity = self.appreciation + self.principle_paid + home_investment.down_payment
        self.home_investment_value = self.equity - self.net_expenses - self.sale_closing_cost
        self.home_investment_growth = DecimalPercent(
            self.home_investment_value / home_investment.initial_cost * 100 - 100
        )
        self.index_fund_value = compound_interest(
            principle=index_fund_value + self.monthly_cashflow,
            interest_rate=home_investment.index_fund_annual_return_rate,
            years=Decimal(1 / c.MONTHS_PER_YEAR),
            number=Decimal(c.MONTHS_PER_YEAR)
        )
        self.index_fund_growth = DecimalPercent(self.index_fund_value / home_investment.initial_cost * 100 - 100)
        self.home_investment_vs_index_fund_growth = self.home_investment_growth - self.index_fund_growth

    def is_last_month(self):
        return self._home_investment.loan_term_months == self.month

    def is_full_year(self):
        return self.month % c.MONTHS_PER_YEAR == 0

    def is_new_year(self):
        return self.month % c.MONTHS_PER_YEAR == 1
