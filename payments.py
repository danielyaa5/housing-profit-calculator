import decimal

import yaml

import mortgage
from helpers import dollar

state_taxes = yaml.safe_load(open('./taxes/state/ca.yaml'))
federal_taxes = yaml.safe_load(open('./taxes/federal.yaml'))


class Payments:
    def __init__(
            self,
            interest_rate,
            loan_term_months,
            loan_amount,
            federal_tax_rate,
            state_tax_rate,
            property_tax_rate,
            homeowners_insurance_rate,
            purchase_price,
            monthly_rent,
            tenant_rent,
            yearly_income,
    ):
        self._interest_rate = interest_rate
        self._loan_term_months = loan_term_months
        self._loan_amount = loan_amount
        self._federal_tax_rate = federal_tax_rate
        self._state_tax_rate = state_tax_rate
        self._property_tax_rate = property_tax_rate
        self._homeowners_insurance_rate = homeowners_insurance_rate
        self._purchase_price = purchase_price
        self._yearly_income = yearly_income
        self._monthly_rent = monthly_rent
        self._tenant_rent = tenant_rent
        self._down_payment = purchase_price - loan_amount

    def monthly_mortgage_schedule(self):
        mortgage_itr = mortgage.Mortgage(interest=self._interest_rate, amount=self._loan_amount,
                                         months=self._loan_term_months).monthly_payment_schedule()
        max_deductible_mortgage_itr = mortgage.Mortgage(interest=self._interest_rate, amount=750 * 1000,
                                                        months=self._loan_term_months).monthly_payment_schedule()

        for index, payment in enumerate(mortgage_itr):
            month_num = index + 1
            principal, interest = payment
            max_deductible_interest = next(max_deductible_mortgage_itr)[1]
            deductible_interest = min(max_deductible_interest, interest)
            yield month_num, principal, interest, deductible_interest

    def yearly_mortgage_schedule(self):
        yearly_principal = decimal.Decimal(0)
        yearly_interest = decimal.Decimal(0)
        yearly_deductible_interest = decimal.Decimal(0)
        for month_num, principal, interest, deductible_interest in self.monthly_mortgage_schedule():
            yearly_principal += principal
            yearly_interest += interest
            yearly_deductible_interest += deductible_interest
            if month_num % 12 == 0:
                yield (month_num / 12), yearly_principal, yearly_interest, yearly_deductible_interest
                yearly_principal = decimal.Decimal(0)
                yearly_interest = decimal.Decimal(0)
                yearly_deductible_interest = decimal.Decimal(0)

    def tax_deduction_per_year(self):
        result = []
        property_tax = self._property_tax_rate * self._purchase_price
        for year_num, principal, interest, deductible_interest in self.yearly_mortgage_schedule():
            deductible_property_tax = min(property_tax, 10000)
            total_deduction = deductible_property_tax + deductible_interest
            result.append(min(total_deduction, self._yearly_income))

        return result

    def tax_savings_per_year(self, tax_rate, standard_deduction):
        result = []
        for tax_deduction in self.tax_deduction_per_year():
            itemized_savings = tax_rate * tax_deduction
            standard_deduction_savings = tax_rate * standard_deduction
            if itemized_savings > standard_deduction_savings:
                itemized_savings -= standard_deduction_savings
            else:
                itemized_savings = 0

            result.append(itemized_savings)

        return result

    def federal_tax_savings_per_year(self):
        return self.tax_savings_per_year(self._federal_tax_rate, federal_taxes['standard_deduction'])

    def state_tax_savings_per_year(self):
        return self.tax_savings_per_year(self._state_tax_rate, state_taxes['standard_deduction'])

    def principal_after_n_years(self, n):
        total_principal = decimal.Decimal(self._down_payment)
        for monthly_payment in self.monthly_payment_schedule(years=n):
            total_principal += monthly_payment['principal']

        return dollar(total_principal)

    def non_principal_cost_after_n_years(self, n):
        total_cost = decimal.Decimal(0)
        for monthly_payment in self.monthly_payment_schedule(years=n):
            total_cost += monthly_payment['total_with_savings_minus_principal']

        return dollar(total_cost)

    def monthly_payment_schedule(self, years=None, months=None):
        yearly_federal_tax_savings = self.federal_tax_savings_per_year()
        yearly_state_tax_savings = self.state_tax_savings_per_year()
        for month_num, principal, interest, deductible_interest in self.monthly_mortgage_schedule():
            year_num = (month_num - 1) // 12 + 1
            if years and year_num > years:
                return

            if months and month_num > months:
                return

            federal_tax_savings = yearly_federal_tax_savings[year_num - 1] / 12
            state_tax_savings = yearly_state_tax_savings[year_num - 1] / 12
            total_tax_savings = federal_tax_savings + state_tax_savings
            property_tax = self._property_tax_rate * self._purchase_price / 12
            home_insurance = self._homeowners_insurance_rate * self._purchase_price / 12
            total_without_savings = principal + interest + property_tax + home_insurance
            total_with_savings = total_without_savings - total_tax_savings - self._monthly_rent - self._tenant_rent
            total_with_savings_minus_principal = total_with_savings - principal
            yield {
                'month': month_num,
                'principal': principal,
                'interest': interest,
                'deductible_interest': deductible_interest,
                'property_tax': property_tax,
                'home_insurance': home_insurance,
                'federal_tax_savings': federal_tax_savings,
                'state_tax_savings': state_tax_savings,
                'total_tax_savings': total_tax_savings,
                'total_without_savings': total_without_savings,
                'total_with_savings': total_with_savings,
                'total_with_savings_minus_principal': total_with_savings_minus_principal,
            }
