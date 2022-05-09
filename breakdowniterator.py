from __future__ import annotations

import os
import pathlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pandas as pd
from tabulate import tabulate

if TYPE_CHECKING:
    from investmentbreakdown import InvestmentBreakdown


class BreakdownIterator(ABC):
    def __init__(self, investment_breakdown: InvestmentBreakdown, dollar_decimal_to_str):
        self._investment_breakdown = investment_breakdown
        self._dollar_decimal_to_str = dollar_decimal_to_str

    @abstractmethod
    def generator(self):
        pass

    def list(self):
        return list(self.generator())

    def df(self):
        return pd.DataFrame(self.generator())

    def tabulate(self):
        return tabulate(self.df(), headers='keys', showindex=False)

    def _csv(self, time):
        dirname = pathlib.Path(__file__).parent.resolve()
        output_path = os.path.join(dirname, 'output', f'{self._investment_breakdown.scenario_name}_{time}.csv')
        print(f'Outputting {time} breakdown to {output_path}\n')
        return self.df().to_csv(output_path, index=False)
