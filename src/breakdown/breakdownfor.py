from __future__ import annotations

import functools
import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generator, Literal

import pandas as pd
from tabulate import tabulate

from src.breakdown.row import BreakdownRow
from src.helpers import rel

if TYPE_CHECKING:
    from src.homeinvestment import HomeInvestment


class BreakdownFor(ABC, object):
    def __init__(self, home_investment: HomeInvestment, time_length: Literal['month', 'year']):
        self._home_investment = home_investment
        self.time_length = time_length

    @abstractmethod
    def generator(self) -> Generator[BreakdownRow, None, None]:
        raise NotImplementedError

    @functools.cache
    def dicts(self):
        return list(map(lambda bd: bd.dict(), self.list()))

    @functools.cache
    def list(self):
        return list(self.generator())

    def df(self, columns=None):
        df = pd.DataFrame(self.dicts())
        return df[columns] if columns else df

    def tabulate(self):
        return tabulate(self.df(), headers='keys', showindex=False)

    def _csv(self, filename, columns=None):
        output_path = rel('../../output', self._home_investment.scenario_name, self.time_length, filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f'Outputting {filename} to {output_path}\n')
        self.df(columns).to_csv(output_path, index=False)
        return output_path

    def csv(self):
        filename = 'full.csv'
        output_path = self._csv(filename)
        return output_path

    def csv_operating_cost(self):
        columns = [
            'month',
            'year',
            'principle',
            'interest',
            'mortgage',
            'property_tax',
            'hoi',
            'hoa',
            'vacancy',
            'maintenance',
            'management_fee',
            'operating_cost',
            'net_operating_cost',
        ]

        filename = 'operating_cost.csv'
        output_path = self._csv(filename=filename, columns=columns)
        return output_path

    def csv_income(self):
        columns = [
            'month',
            'year',
            'deductible_interest',
            'tax_savings',
            'rent',
            'tenant_rent',
            'income',
            'net_income',
        ]

        filename = 'income.csv'
        output_path = self._csv(filename=filename, columns=columns)
        return output_path

    def csv_cashflow(self):
        columns = [
            'month',
            'year',
            'income',
            'adjusted_income',
            'mortgage',
            'operating_cost',
            'expenses',
            'cashflow',
        ]

        if self.time_length == 'year':
            columns.append('cash_on_cash_return')

        columns += [
            'equity',
            'cash_to_receive'
        ]

        filename = 'cashflow.csv'
        output_path = self._csv(filename=filename, columns=columns)
        return output_path

    def csv_investment(self):
        columns = [
            'month',
            'year',
            'cashflow',
            'net_cashflow',
            'equity',
            'cashflow_surplus_index_fund_value',
            'sale_closing_cost',
            'cash_to_receive',
            'home_investment_value',
            'home_roi',
            'index_fund_value',
            'index_fund_roi',
            'score'
        ]
        if self.time_length == 'year':
            columns.append('cash_on_cash_return')

        filename = 'investment.csv'
        output_path = self._csv(filename=filename, columns=columns)
        return output_path

    def csv_investment_short(self):
        columns = [
            'cashflow',
            'net_cashflow',
            'appreciated_price',
            'equity',
            'home_investment_value',
            'home_roi',
            'index_fund_value',
            'index_fund_roi',
            'score'
        ]

        filename = 'investment_short.csv'
        output_path = self._csv(filename=filename, columns=columns)
        return output_path
