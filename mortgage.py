from __future__ import print_function

import argparse
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal

from decimaldollar import DecimalDollar
import constants as c


class MortgageWithoutDeductible:
    def __init__(self, interest, months, amount):
        self._interest = float(interest)
        self._months = int(months)
        self._amount = DecimalDollar(amount)

    def rate(self):
        return self._interest

    def month_growth(self):
        return 1. + self._interest / c.MONTHS_PER_YEAR

    def apy(self):
        return self.month_growth() ** c.MONTHS_PER_YEAR - 1

    def loan_years(self):
        return float(self._months) / c.MONTHS_PER_YEAR

    def loan_months(self):
        return self._months

    def amount(self):
        return self._amount

    def monthly_payment(self):
        pre_amt = float(self.amount()) * self.rate() / (
                float(c.MONTHS_PER_YEAR) * (1. - (1. / self.month_growth()) ** self.loan_months()))
        return DecimalDollar(pre_amt).quantize(c.TENTH_PLACE_QUANTIZE, rounding=ROUND_CEILING)

    def total_value(self, m_payment):
        return m_payment / self.rate() * (
                float(c.MONTHS_PER_YEAR) * (1. - (1. / self.month_growth()) ** self.loan_months()))

    def annual_payment(self):
        return self.monthly_payment() * c.MONTHS_PER_YEAR

    def total_payout(self):
        return self.monthly_payment() * self.loan_months()

    def monthly_payment_schedule(self):
        monthly = self.monthly_payment()
        balance = self.amount()
        rate = Decimal(str(self.rate())).quantize(Decimal('.000001'))
        while True:
            interest_unrounded = balance * rate * Decimal(1) / c.MONTHS_PER_YEAR
            interest = DecimalDollar(interest_unrounded).quantize(c.TENTH_PLACE_QUANTIZE, rounding=ROUND_HALF_UP)
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


class Mortgage(MortgageWithoutDeductible):
    def __init__(self, interest_rate, loan_term_months, loan_amount):
        self.max_deductible_mortgage = MortgageWithoutDeductible(
            interest=interest_rate, amount=750000, months=loan_term_months
        )
        super().__init__(interest_rate, loan_term_months, loan_amount)

    def monthly_mortgage_schedule(self):
        max_deductible_mortgage_itr = self.max_deductible_mortgage.monthly_payment_schedule()

        for index, payment in enumerate(super().monthly_payment_schedule()):
            month_num = index + 1
            principle, interest = payment
            max_deductible_interest = next(max_deductible_mortgage_itr)[1]
            deductible_interest = min(max_deductible_interest, interest)
            yield month_num, principle, interest, deductible_interest

    def yearly_mortgage_schedule(self):
        yearly_principle = DecimalDollar(0)
        yearly_interest = DecimalDollar(0)
        yearly_deductible_interest = DecimalDollar(0)
        for month_num, principle, interest, deductible_interest in self.monthly_mortgage_schedule():
            yearly_principle += principle
            yearly_interest += interest
            yearly_deductible_interest += deductible_interest
            if month_num % 12 == 0:
                yield (month_num / 12), yearly_principle, yearly_interest, yearly_deductible_interest
                yearly_principle = DecimalDollar(0)
                yearly_interest = DecimalDollar(0)
                yearly_deductible_interest = DecimalDollar(0)


def print_summary(m):
    print('{0:>25s}:  {1:>12.6f}'.format('Rate', m.rate()))
    print('{0:>25s}:  {1:>12.6f}'.format('Month Growth', m.month_growth()))
    print('{0:>25s}:  {1:>12.6f}'.format('APY', m.apy()))
    print('{0:>25s}:  {1:>12.0f}'.format('Payoff Years', m.loan_years()))
    print('{0:>25s}:  {1:>12.0f}'.format('Payoff Months', m.loan_months()))
    print('{0:>25s}:  {1:>12.2f}'.format('Amount', m.amount()))
    print('{0:>25s}:  {1:>12.2f}'.format('Monthly Payment', m.monthly_payment()))
    print('{0:>25s}:  {1:>12.2f}'.format('Annual Payment', m.annual_payment()))
    print('{0:>25s}:  {1:>12.2f}'.format('Total Payout', m.total_payout()))


def main():
    parser = argparse.ArgumentParser(description='Mortgage Amortization Tools')
    parser.add_argument('-i', '--interest', default=6, dest='interest')
    parser.add_argument('-y', '--loan-_years', default=30, dest='_years')
    parser.add_argument('-m', '--loan-_months', default=None, dest='_months')
    parser.add_argument('-a', '--amount', default=100000, dest='amount')
    args = parser.parse_args()

    if args.months:
        m = MortgageWithoutDeductible(float(args.interest) / 100, float(args.months), args.amount)
    else:
        m = MortgageWithoutDeductible(float(args.interest) / 100, float(args.years) * c.MONTHS_PER_YEAR, args.amount)

    print_summary(m)


if __name__ == '__main__':
    main()
