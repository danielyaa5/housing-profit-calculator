import src.constants as c
from src.decimal.dollar import Dollar
from src.helpers import compound_interest


class DollarCompYearly(object):
    def __init__(self, v0, rate):
        self.initial_value = Dollar(v0)
        self.rate = rate

    def __getitem__(self, num_months):
        if num_months == 0:
            return Dollar(0)
        year = (num_months - 1) // c.MONTHS_PER_YEAR
        new_value = compound_interest(self.initial_value, self.rate, year, 1)
        return Dollar(new_value)

    def year(self, num_years):
        new_value = compound_interest(self.initial_value, self.rate, num_years, 1)
        return Dollar(new_value)

    def full_year(self, num_years):
        return self.year(num_years) * c.MONTHS_PER_YEAR
