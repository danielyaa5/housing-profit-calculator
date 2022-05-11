from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from investmentsummary import InvestmentSummary
from yearsummaryrow import YearSummaryRow

if TYPE_CHECKING:
    from homeinvestment import HomeInvestment


class YearlySummary(InvestmentSummary):
    def __init__(self, home_investment: HomeInvestment):
        super().__init__(home_investment, 'year')

    def generator(self) -> Generator[YearSummaryRow, None, None]:
        months = []
        for month_bd in self._home_investment.monthly().generator():
            months.append(month_bd)

            if month_bd.is_last_month() or month_bd.is_full_year():
                yield YearSummaryRow(months)
                months = []
