from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import src.constants as c
from src.breakdown.breakdownfor import BreakdownFor
from src.breakdown.rowmonth import RowMonth
from src.decimal.dollar import Dollar

if TYPE_CHECKING:
    from src.homeinvestment import HomeInvestment


class BreakdownForMonth(BreakdownFor):
    def __init__(self, home_investment: HomeInvestment):
        super().__init__(home_investment, 'month')

    def generator(self) -> Generator[RowMonth, None, None]:
        mortgage = self._home_investment.mortgage
        
        last = RowMonth(
            home_investment=self._home_investment,
            month=0,
            year=0,
            principle=Dollar(0),
            interest=Dollar(0),
            deductible_interest=Dollar(0),
            net_operating_cost=Dollar(0),
            net_income=Dollar(0),
            net_cashflow=-Dollar(0),
            principle_paid=Dollar(0),
            interest_paid=Dollar(0),
            appreciated_price=Dollar(0),
            index_fund_value=Dollar(0),
            cashflow_surplus_index_fund_value=Dollar(0)
        )
        yield last

        for month, principle, interest, deductible_interest in mortgage.monthly_mortgage_schedule():
            year = (month - 1) // c.MONTHS_PER_YEAR + 1
            last = RowMonth(
                home_investment=self._home_investment,
                month=month,
                year=year,
                principle=principle,
                interest=interest,
                deductible_interest=deductible_interest,
                net_operating_cost=last.net_operating_cost,
                net_income=last.net_income,
                net_cashflow=last.net_cashflow,
                principle_paid=last.principle_paid,
                interest_paid=last.interest_paid,
                appreciated_price=last.appreciated_price,
                index_fund_value=last.index_fund_value,
                cashflow_surplus_index_fund_value=last.cashflow_surplus_index_fund_value
            )
            yield last
