from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import constants as c
from decimalpercent import DecimalPercent
from helpers import compound_interest
from investmentsummary import SummaryRow

if TYPE_CHECKING:
    from homeinvestment import HomeInvestment


class MonthSummaryRow(SummaryRow):
    def __init__(
            self,
            home_investment: HomeInvestment,
            month,
            year,
            principle,
            interest,
            deductible_interest,
            net_expenses,
            net_cashflow_positive,
            net_cashflow,
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
        self.monthly_hoi = home_investment.hoi
        self.monthly_hoa = home_investment.hoa
        self.monthly_vacancy = home_investment.vacancy(year)
        self.monthly_maintenance_fee = home_investment.maintenance_fee
        self.monthly_expenses = sum([
            self.monthly_interest,
            self.monthly_property_tax,
            self.monthly_hoi,
            self.monthly_hoa,
            self.monthly_vacancy,
            self.monthly_maintenance_fee
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
        self.net_cashflow_positive = net_cashflow_positive + self.monthly_cashflow_positive
        self.net_expenses = self.monthly_expenses + net_expenses
        self.monthly_cashflow = self.monthly_cashflow_positive - self.monthly_cashflow_negative
        self.net_cashflow = net_cashflow + self.monthly_cashflow

        # Home Investment Value
        self.monthly_appreciation = home_investment.monthly_appreciation(year)
        self.appreciated_price = appreciated_price + self.monthly_appreciation
        self.appreciation = self.appreciated_price - home_investment.purchase_price
        self.principle_paid = principle_paid + principle
        self.sale_closing_cost = self.appreciated_price * home_investment.sale_closing_cost_rate
        self.equity = self.appreciation + self.principle_paid + home_investment.down_payment
        self.home_investment_value = self.net_cashflow_positive + self.equity - self.net_expenses - self.sale_closing_cost

        if self.monthly_cashflow > 0:
            raise Exception(f'Monthly Cashflow is positive: {self.monthly_cashflow}, logic for this has not been implemented')

        # Index Fund Value
        self.index_fund_value = compound_interest(
            principle=index_fund_value + -self.monthly_cashflow,
            interest_rate=home_investment.index_fund_annual_return_rate,
            years=Decimal(1 / c.MONTHS_PER_YEAR),
            number=Decimal(c.MONTHS_PER_YEAR)
        )

        # Home Investment vs Index Fund ROI Comparison
        self.home_roi = DecimalPercent(self.home_investment_value / home_investment.initial_cost * 100 - 100)
        self.index_fund_roi = DecimalPercent(self.index_fund_value / home_investment.initial_cost * 100 - 100)
        self.home_investment_vs_index_fund_roi = self.home_roi - self.index_fund_roi

    def is_last_month(self):
        return self._home_investment.loan_term_months == self.month

    def is_full_year(self):
        return self.month % c.MONTHS_PER_YEAR == 0

    def is_new_year(self):
        return self.month % c.MONTHS_PER_YEAR == 1
