from __future__ import annotations

from typing import TYPE_CHECKING, Generator

from investmentsummary import InvestmentSummary, SummaryRow
from monthlysummary import Month

if TYPE_CHECKING:
    from homeinvestment import HomeInvestment


class YearlySummary(InvestmentSummary):
    def __init__(self, home_investment: HomeInvestment, years=None):
        super().__init__(home_investment)
        self._years = years

    def generator(self) -> Generator[Year, None, None]:
        months = []
        for month_bd in self._home_investment.monthly().generator():
            months.append(month_bd)

            if month_bd.is_last_month() or month_bd.is_full_year():
                yield Year(months)
                months = []

    def csv(self):
        return self._csv('yearly')


class Year(SummaryRow):
    def __init__(self, months: list[Month]):
        for month in months:
            for k, v in month.__dict__.items():
                if k.startswith('_'):
                    continue

                if k.startswith('monthly_') and not month.is_new_year():
                    setattr(self, self._key(k), getattr(self, self._key(k)) + v)
                else:
                    setattr(self, self._key(k), v)

    @staticmethod
    def _key(k):
        return f'yearly_{k[8:]}' if k.startswith('monthly_') else k
