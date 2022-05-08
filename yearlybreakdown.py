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


def _monthly_generator(investment_breakdown: InvestmentBreakdown):
    for breakdown in investment_breakdown.monthly(dollar_decimal_to_str=False).generator():
        is_last_month = investment_breakdown.loan_term_months == breakdown['month']
        is_full_year = breakdown['month'] % c.MONTHS_PER_YEAR == 0
        is_new_year = breakdown['month'] % c.MONTHS_PER_YEAR == 1
        yield is_last_month, is_full_year, is_new_year, breakdown


class YearlyBreakdown:
    def __init__(self, investment_breakdown: InvestmentBreakdown, years=None, dollar_decimal_to_str=True):
        self.investment_breakdown = investment_breakdown
        self.years = years
        self.dollar_decimal_to_str = dollar_decimal_to_str

    def generator(self):
        yearly_breakdown = None
        for is_last_month, is_full_year, is_new_year, month_bd in _monthly_generator(self.investment_breakdown):
            def _sum(key):
                return month_bd[key] if is_new_year else yearly_breakdown[key] + month_bd[key]

            yearly_breakdown = {
                'year': month_bd['year'],
                'interest': _sum('interest'),
                'principal': _sum('principal'),
                'principal_collected': month_bd['principal_collected'],
                'deductible_interest': _sum('deductible_interest'),
                'property_tax': _sum('property_tax'),
                'home_insurance': _sum('home_insurance'),
                'federal_tax_savings': _sum('federal_tax_savings'),
                'state_tax_savings': _sum('state_tax_savings'),
                'tax_savings': _sum('tax_savings'),
                'savings': _sum('savings'),
                'appreciation': _sum('appreciation'),
                'appreciated_price': month_bd['appreciated_price'],
                'sale_closing_cost': month_bd['sale_closing_cost'],
                'sale_profit': month_bd['sale_profit'],
                'sale_profit_per_year': month_bd['sale_profit_per_month'] * c.MONTHS_PER_YEAR,
                'mortgage': _sum('mortgage'),
                'cost': _sum('cost'),
                'cost_with_savings': _sum('cost_with_savings'),
                'cost_with_savings_minus_principal': _sum('cost_with_savings_minus_principal'),
            }
            if is_last_month or is_full_year:
                if self.dollar_decimal_to_str:
                    yearly_breakdown = {
                        k: (f'{v}' if isinstance(v, DollarDecimal) else v) for (k, v) in yearly_breakdown.items()
                    }

                yield yearly_breakdown

    def list(self):
        return list(self.generator())

    def df(self):
        return pd.DataFrame(self.generator())

    def csv(self):
        dirname = pathlib.Path(__file__).parent.resolve()
        output_path = os.path.join(dirname, 'output', f'{self.investment_breakdown.scenario_name}_yearly.csv')
        print(f'Outputting yearly breakdown to {output_path}\n')
        return self.df().to_csv(output_path, index=False)

    def tabulate(self):
        return tabulate(self.df(), headers='keys', showindex=False)
