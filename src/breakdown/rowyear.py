from src.breakdown.row import BreakdownRow
from src.breakdown.rowmonth import RowMonth


class RowYear(BreakdownRow):
    def __init__(self, months: list[RowMonth]):
        for month in months:
            for month_k, v in month.__dict__.items():
                if month_k.startswith('_'):
                    continue

                year_k = f'yearly_{month_k[8:]}' if month_k.startswith('monthly_') else month_k
                if month_k.startswith('monthly_') and not month.is_new_year():
                    setattr(self, year_k, getattr(self, year_k) + v)
                else:
                    setattr(self, year_k, v)
