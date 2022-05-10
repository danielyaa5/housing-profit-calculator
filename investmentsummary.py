from __future__ import annotations

import os
import pathlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generator

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
    def __init__(self, home_investment: HomeInvestment):
        self._home_investment = home_investment

    @abstractmethod
    def generator(self) -> Generator[SummaryRow, None, None]:
        raise NotImplementedError

    def dicts(self):
        return map(lambda bd: bd.dict(), self.generator())

    def list(self):
        return list(self.generator())

    def df(self):
        return pd.DataFrame(self.dicts())

    def tabulate(self):
        return tabulate(self.df(), headers='keys', showindex=False)

    @abstractmethod
    def csv(self):
        raise NotImplementedError

    def _csv(self, time):
        dirname = pathlib.Path(__file__).parent.resolve()
        output_path = os.path.join(dirname, 'output', f'{self._home_investment.scenario_name}_{time}.csv')
        print(f'Outputting {time} breakdown to {output_path}\n')
        return self.df().to_csv(output_path, index=False)
