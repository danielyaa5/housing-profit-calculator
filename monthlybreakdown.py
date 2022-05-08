from __future__ import annotations

import os
import pathlib
from typing import TYPE_CHECKING

import pandas as pd
from tabulate import tabulate
import constants as c

from dollardecimal import DollarDecimal

if TYPE_CHECKING:
    from investmentbreakdown import InvestmentBreakdown


class MonthlyBreakdown:
    def __init__(self, investment_breakdown: InvestmentBreakdown, years=None, months=None, dollar_decimal_to_str=True):
        self.investment_breakdown = investment_breakdown
        self.years = years
        self.months = months
        self.dollar_decimal_to_str = dollar_decimal_to_str

    def generator(self):
        ib = self.investment_breakdown
        principal_collected = DollarDecimal(ib.down_payment)
        total_cost_with_savings_minus_principal = DollarDecimal(0)
        for month_num, principal, interest, deductible_interest in ib.mortgage.monthly_mortgage_schedule():
            year_num = (month_num - 1) // c.MONTHS_PER_YEAR + 1
            if self.years and year_num > self.years:
                return

            if self.months and month_num > self.months:
                return

            federal_tax_savings = ib.federal_tax_savings(year_num) / c.MONTHS_PER_YEAR
            state_tax_savings = ib.state_tax_savings(year_num) / 12
            monthly_tax_savings = federal_tax_savings + state_tax_savings
            monthly_savings = monthly_tax_savings + ib.monthly_rent
            if ib.tenant_rent:
                monthly_savings += ib.tenant_rent
            monthly_cost = principal + interest + ib.monthly_property_tax + ib.monthly_home_insurance
            if ib.hoa:
                monthly_cost += ib.hoa
            monthly_cost_with_savings = monthly_cost - monthly_savings
            monthly_cost_with_savings_minus_principal = monthly_cost_with_savings - principal
            principal_collected += principal
            monthly_appreciation = ib.yearly_appreciation(year_num) / c.MONTHS_PER_YEAR
            mortgage = principal + interest
            appreciated_price = ib.appreciated_price(year_num)
            sale_closing_cost = DollarDecimal(appreciated_price * ib.sale_closing_cost_percent / 100)
            total_cost_with_savings_minus_principal += monthly_cost_with_savings_minus_principal
            total_cost = total_cost_with_savings_minus_principal + sale_closing_cost + ib.purchase_closing_cost
            sale_profit = appreciated_price - ib.purchase_price - total_cost + principal_collected
            sale_profit_per_month = sale_profit / month_num
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
                'savings': monthly_savings,
                'appreciation': monthly_appreciation,
                'appreciated_price': appreciated_price,
                'sale_closing_cost': sale_closing_cost,
                'sale_profit': sale_profit,
                'sale_profit_per_month': sale_profit_per_month,
                'mortgage': mortgage,
                'cost': monthly_cost,
                'cost_with_savings': monthly_cost_with_savings,
                'cost_with_savings_minus_principal': monthly_cost_with_savings_minus_principal,
            }

            if self.dollar_decimal_to_str:
                breakdown = {
                    k: (f'{v}' if isinstance(v, DollarDecimal) else v) for (k, v) in breakdown.items()
                }

            yield breakdown

    def list(self):
        return list(self.generator())

    def df(self):
        return pd.DataFrame(self.generator())

    def csv(self):
        dirname = pathlib.Path(__file__).parent.resolve()
        output_path = os.path.join(dirname, 'output', f'{self.investment_breakdown.scenario_name}_monthly.csv')
        print(f'Outputting monthly breakdown to {output_path}\n')
        return self.df().to_csv(output_path, index=False)

    def tabulate(self):
        return tabulate(self.df(), headers='keys', showindex=False)
