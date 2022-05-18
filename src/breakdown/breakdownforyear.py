from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from src.breakdown.breakdownfor import BreakdownFor
from src.breakdown.rowyear import RowYear

if TYPE_CHECKING:
    from src.homeinvestment import HomeInvestment


class BreakdownForYear(BreakdownFor):
    def __init__(self, home_investment: HomeInvestment):
        super().__init__(home_investment, 'year')

    def generator(self) -> Generator[RowYear, None, None]:
        months = []
        for month_bd in self._home_investment.breakdown().monthly().generator():
            months.append(month_bd)

            if month_bd.is_last_month() or month_bd.is_full_year():
                yield RowYear(months)
                months = []
