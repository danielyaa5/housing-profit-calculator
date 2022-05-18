from __future__ import print_function

from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal
from typing import Callable

import src.constants as c
from src.decimal.dollar import Dollar
from src.decimal.rate import Rate
from src.purchase import Purchase


class MortgageBase:
    def __init__(self, interest_rate: Rate, loan_term_years: int, loan_amount: Dollar):
        self.interest_rate = interest_rate
        self.loan_term_years = int(loan_term_years)
        self.loan_term_months = self.loan_term_years * c.MONTHS_PER_YEAR
        self.loan_amount = loan_amount
        self.month_growth = 1. + float(self.interest_rate) / c.MONTHS_PER_YEAR
        self.apy = self.month_growth ** c.MONTHS_PER_YEAR - 1

    def monthly_payment(self):
        pre_amt = float(self.loan_amount) * float(self.interest_rate) / (
                float(c.MONTHS_PER_YEAR) * (1. - (1. / self.month_growth) ** self.loan_term_months))
        return Dollar(pre_amt).quantize(c.TENTH_PLACE_QUANTIZE, rounding=ROUND_CEILING)

    def monthly_payment_schedule(self):
        monthly = self.monthly_payment()
        balance = self.loan_amount
        rate = Decimal(self.interest_rate).quantize(Decimal('.000001'))
        while True:
            interest_unrounded = balance * rate * Decimal(1) / c.MONTHS_PER_YEAR
            interest = Dollar(interest_unrounded).quantize(c.TENTH_PLACE_QUANTIZE, rounding=ROUND_HALF_UP)
            if monthly >= balance + interest:
                yield balance, interest
                break
            principle = monthly - interest
            yield principle, interest
            balance -= principle

    def yearly_payment_schedule(self):
        yearly_principle = Decimal(0)
        yearly_interest = Decimal(0)
        for index, payment in enumerate(self.monthly_payment_schedule()):
            month_num = index + 1
            monthly_principle, monthly_interest = payment
            yearly_principle += monthly_principle
            yearly_interest += monthly_interest
            if month_num % 12 == 0:
                yield yearly_principle, yearly_interest
                yearly_principle = Decimal(0)
                yearly_interest = Decimal(0)


class Mortgage(MortgageBase):
    def __init__(self, interest_rate, loan_term_years, purchase: Purchase):
        self.max_deductible_mortgage = MortgageBase(
            interest_rate=interest_rate,
            loan_term_years=loan_term_years,
            loan_amount=Dollar(750000)
        )

        super().__init__(
            interest_rate=interest_rate,
            loan_term_years=loan_term_years,
            loan_amount=purchase.price - purchase.down_payment
        )

    def monthly_mortgage_schedule(self):
        max_deductible_mortgage_itr = self.max_deductible_mortgage.monthly_payment_schedule()

        for index, payment in enumerate(super().monthly_payment_schedule()):
            month_num = index + 1
            principle, interest = payment
            max_deductible_interest = next(max_deductible_mortgage_itr)[1]
            deductible_interest = min(max_deductible_interest, interest)
            yield month_num, principle, interest, deductible_interest

    def yearly_mortgage_schedule(self):
        yearly_principle = Dollar(0)
        yearly_interest = Dollar(0)
        yearly_deductible_interest = Dollar(0)
        for month_num, principle, interest, deductible_interest in self.monthly_mortgage_schedule():
            yearly_principle += principle
            yearly_interest += interest
            yearly_deductible_interest += deductible_interest
            if month_num % 12 == 0:
                yield (month_num / 12), yearly_principle, yearly_interest, yearly_deductible_interest
                yearly_principle = Dollar(0)
                yearly_interest = Dollar(0)
                yearly_deductible_interest = Dollar(0)


MortgageFactoryType = Callable[[Purchase], Mortgage]


def mortgage(interest_rate_percent: float, loan_term_years: float) -> MortgageFactoryType:
    assert loan_term_years % 1 == 0, 'loan_term_years must be a whole number'

    def factory(purchase: Purchase) -> Mortgage:
        return Mortgage(
            purchase=purchase,
            interest_rate=Rate(percent=interest_rate_percent),
            loan_term_years=int(loan_term_years),
        )

    return factory
