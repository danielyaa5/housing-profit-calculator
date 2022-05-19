from src.breakdown.row import BreakdownRow
from src.breakdown.rowmonth import RowMonth
from src.decimal.percent import Percent
from src.purchase import Purchase


class RowYear(BreakdownRow):
    def __init__(self, months: list[RowMonth], purchase: Purchase):
        for idx, month in enumerate(months):
            for month_k, v in month.__dict__.items():
                if month_k.startswith('_'):
                    continue

                year_k = f'yearly_{month_k[8:]}' if month_k.startswith('monthly_') else month_k
                if month_k.startswith('monthly_') and not idx == 0:
                    setattr(self, year_k, getattr(self, year_k) + v)
                else:
                    setattr(self, year_k, v)

            if self.year != 0:
                self.cash_on_cash_return = Percent(self.yearly_cashflow / purchase.cost_initial * 100)
