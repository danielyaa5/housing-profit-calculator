from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import constants as c
from decimaldollar import DecimalDollar
from investmentsummary import InvestmentSummary
from monthsummaryrow import MonthSummaryRow

if TYPE_CHECKING:
    from homeinvestment import HomeInvestment


class MonthlySummary(InvestmentSummary):
    def __init__(self, home_investment: HomeInvestment):
        super().__init__(home_investment, 'month')

    def generator(self) -> Generator[MonthSummaryRow, None, None]:
        mortgage = self._home_investment.mortgage
        last = None

        for month, principle, interest, deductible_interest in mortgage.monthly_mortgage_schedule():
            year = (month - 1) // c.MONTHS_PER_YEAR + 1
            last = MonthSummaryRow(
                home_investment=self._home_investment,
                month=month,
                year=year,
                principle=principle,
                interest=interest,
                deductible_interest=deductible_interest,
                net_expenses=last.net_expenses if last else self._home_investment.purchase_closing_cost,
                net_cashflow_positive=last.net_cashflow_positive if last else DecimalDollar(0),
                net_cashflow=last.net_cashflow if last else -self._home_investment.initial_cost,
                principle_paid=last.principle_paid if last else DecimalDollar(0),
                appreciated_price=last.appreciated_price if last else self._home_investment.purchase_price,
                index_fund_value=last.index_fund_value if last else self._home_investment.initial_cost,
            )
            yield last
