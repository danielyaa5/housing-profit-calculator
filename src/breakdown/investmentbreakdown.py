from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from src.breakdown.breakdownformonth import BreakdownForMonth
from src.breakdown.breakdownforyear import BreakdownForYear

if TYPE_CHECKING:
    from src.homeinvestment import HomeInvestment


class InvestmentBreakdown(object):
    def __init__(self, home_investment: HomeInvestment):
        self._home_investment = home_investment
        self.monthly = BreakdownForMonth(home_investment)
        self.yearly = BreakdownForYear(home_investment)
