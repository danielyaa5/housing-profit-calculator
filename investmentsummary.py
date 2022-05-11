from __future__ import annotations

import functools
import os
import pathlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generator, Literal

import pandas as pd
from tabulate import tabulate

from decimaldollar import DecimalDollar
from decimalpercent import DecimalPercent

if TYPE_CHECKING:
    from homeinvestment import HomeInvestment


class SummaryRow(ABC, object):
    def dict(self):
        def should_fmt(v):
            return isinstance(v, DecimalDollar) or isinstance(v, DecimalPercent)

        def _key(k):
            if k.startswith('monthly_'):
                return k[8:]
            if k.startswith('yearly_'):
                return k[7:]
            return k

        return {
            _key(k): (f'{v}' if should_fmt(v) else v) for (k, v) in self.__dict__.items() if not k.startswith('_')
        }


class InvestmentSummary(ABC, object):
    def __init__(self, home_investment: HomeInvestment, time_length: Literal['month', 'year']):
        self._home_investment = home_investment
        self.time_length = time_length

    @abstractmethod
    def generator(self) -> Generator[SummaryRow, None, None]:
        raise NotImplementedError

    @functools.cache
    def dicts(self):
        return list(map(lambda bd: bd.dict(), self.generator()))

    @functools.cache
    def list(self):
        return list(self.generator())

    def df(self, columns=None):
        df = pd.DataFrame(self.dicts())
        return df[columns] if columns else df

    def tabulate(self):
        return tabulate(self.df(), headers='keys', showindex=False)

    def csv(self):
        filename = f'{self._home_investment.scenario_name}_{self.time_length}.csv'
        output_path = self._csv(filename)
        return output_path

    def csv_cashflow_negative(self):
        columns = [
            'month',
            'principle',
            'interest',
            'mortgage',
            'property_tax',
            'hoi',
            'hoa',
            'vacancy',
            'maintenance_fee',
            'expenses',
            'net_expenses',
            'cashflow_negative',
        ]

        filename = f'{self._home_investment.scenario_name}_{self.time_length}_cf_neg.csv'
        output_path = self._csv(filename=filename, columns=columns)
        return output_path

    def csv_cashflow_positive(self):
        columns = [
            'deductible_interest',
            'state_tax_savings',
            'federal_tax_savings',
            'tax_savings',
            'rent',
            'tenant_rent',
            'cashflow_positive',
            'net_cashflow_positive',
        ]

        filename = f'{self._home_investment.scenario_name}_{self.time_length}_cf_pos.csv'
        output_path = self._csv(filename=filename, columns=columns)
        return output_path

    def csv_investment(self):
        columns = [
            'expenses',
            'net_expenses',
            'cashflow_positive',
            'net_cashflow_positive',
            'cashflow',
            'net_cashflow',
            'appreciation',
            'appreciated_price',
            'principle_paid',
            'sale_closing_cost',
            'equity',
            'home_investment_value',
            'home_roi',
            'index_fund_value',
            'index_fund_roi',
            'home_investment_vs_index_fund_roi'
        ]

        filename = f'{self._home_investment.scenario_name}_{self.time_length}_investment.csv'
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
            'home_investment_vs_index_fund_roi'
        ]

        filename = f'{self._home_investment.scenario_name}_{self.time_length}_investment_short.csv'
        output_path = self._csv(filename=filename, columns=columns)
        return output_path

    def _csv(self, filename, columns=None):
        dirname = pathlib.Path(__file__).parent.resolve()
        output_path = os.path.join(dirname, 'output', filename)
        print(f'Outputting {filename} to {output_path}\n')
        self.df(columns).to_csv(output_path, index=False)
        return output_path
