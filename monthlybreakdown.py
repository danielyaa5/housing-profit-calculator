from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import constants as c
from breakdowniterator import BreakdownIterator
from dollardecimal import DollarDecimal
from helpers import compound_interest
from percentdecimal import PercentDecimal

if TYPE_CHECKING:
    from investmentbreakdown import InvestmentBreakdown


class MonthlyBreakdown(BreakdownIterator):
    def __init__(self, investment_breakdown: InvestmentBreakdown, years=None, months=None, dollar_decimal_to_str=True):
        super().__init__(investment_breakdown, dollar_decimal_to_str)
        self._years = years
        self._months = months

    def generator(self):
        ib = self._investment_breakdown
        principal_collected = DollarDecimal(ib.down_payment)
        total_cost_with_savings = DollarDecimal(0)
        tenant_rent = ib.tenant_rent or DollarDecimal(0)
        appreciated_price = ib.purchase_price
        hoa = ib.hoa or 0
        initial_index_fund_balance = DollarDecimal(ib.down_payment - ib.purchase_closing_cost)
        index_fund_value = initial_index_fund_balance
        initial_home_investment = ib.down_payment + ib.purchase_closing_cost

        for month_num, principal, interest, deductible_interest in ib.mortgage.monthly_mortgage_schedule():
            year_num = (month_num - 1) // c.MONTHS_PER_YEAR + 1
            if self._years and year_num > self._years:
                return

            if self._months and month_num > self._months:
                return

            federal_tax_savings = ib.federal_tax_savings(year_num) / c.MONTHS_PER_YEAR
            state_tax_savings = ib.state_tax_savings(year_num) / c.MONTHS_PER_YEAR
            monthly_tax_savings = federal_tax_savings + state_tax_savings
            monthly_savings = monthly_tax_savings + ib.rent(year_num) + tenant_rent
            monthly_cost = principal + interest + ib.monthly_property_tax + ib.monthly_home_insurance + hoa
            monthly_cost_with_savings = monthly_cost - monthly_savings
            monthly_cost_with_savings_minus_principal = monthly_cost_with_savings - principal
            principal_collected += principal
            monthly_appreciation = ib.monthly_appreciation(year_num)
            mortgage = principal + interest
            appreciated_price += monthly_appreciation
            sale_closing_cost = DollarDecimal(appreciated_price * ib.sale_closing_cost_percent / 100)
            index_fund_value = compound_interest(
                principal=index_fund_value + monthly_cost_with_savings,
                interest_rate=ib.index_fund_annual_return_rate,
                years=Decimal(1 / c.MONTHS_PER_YEAR),
                number=Decimal(c.MONTHS_PER_YEAR)
            )
            total_cost_with_savings += monthly_cost_with_savings
            sale_costs = total_cost_with_savings + sale_closing_cost + ib.purchase_closing_cost
            # print(json.dumps({
            #     'appreciated_price': appreciated_price,
            #     'purchase_price': ib.purchase_price,
            #     'total_cost_with_savings': total_cost_with_savings,
            #     'sale_costs': sale_costs,
            #     'principal_collected': principal_collected
            # }, default=str, indent=2))
            home_investment_value = appreciated_price - ib.purchase_price - sale_costs + principal_collected
            home_investment_growth = PercentDecimal(home_investment_value / initial_home_investment * 100 - 100)
            index_fund_growth = PercentDecimal(index_fund_value / initial_index_fund_balance * 100 - 100)
            home_investment_vs_index_fund_growth = home_investment_growth - index_fund_growth

            breakdown = {
                'month': month_num,
                'year': year_num,
                'interest': interest,
                'principal': principal,
                'principal_collected': principal_collected,
                'deductible_interest': deductible_interest,
                'property_tax': ib.monthly_property_tax,
                'home_insurance': ib.monthly_home_insurance,
                'federal_tax_savings': federal_tax_savings,
                'state_tax_savings': state_tax_savings,
                'tax_savings': monthly_tax_savings,
                'rent': ib.rent(year_num),
                'savings': monthly_savings,
                'appreciation': monthly_appreciation,
                'appreciated_price': appreciated_price,
                'sale_closing_cost': sale_closing_cost,
                'mortgage': mortgage,
                'cost': monthly_cost,
                'cost_with_savings': monthly_cost_with_savings,
                'cost_with_savings_minus_principal': monthly_cost_with_savings_minus_principal,
                'index_fund_value': index_fund_value,
                'home_investment_value': home_investment_value,
                'index_fund_growth': index_fund_growth,
                'home_investment_growth': home_investment_growth,
                'home_investment_vs_index_fund_growth': home_investment_vs_index_fund_growth,
            }

            if self._dollar_decimal_to_str:
                def should_fmt(v):
                    return isinstance(v, DollarDecimal) or isinstance(v, PercentDecimal)

                breakdown = {
                    k: (f'{v}' if should_fmt(v) else v) for (k, v) in breakdown.items()
                }

            yield breakdown

    def csv(self):
        return self._csv('monthly')
