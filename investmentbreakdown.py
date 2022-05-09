from decimal import Decimal

import pandas as pd
import yaml
from tabulate import tabulate

import constants as c
from dollardecimal import DollarDecimal
from helpers import rangei, compound_interest
from monthlybreakdown import MonthlyBreakdown
from mortgage import Mortgage
from yearlybreakdown import YearlyBreakdown

state_taxes = yaml.safe_load(open('./taxes/state/ca.yaml'))
federal_taxes = yaml.safe_load(open('./taxes/federal.yaml'))


class InvestmentBreakdown:
    def __init__(
            self,
            interest_rate_percent,
            loan_term_years,
            down_payment_amount,
            down_payment_percent,
            federal_tax_rate_percent,
            state_tax_rate_percent,
            property_tax_rate_percent,
            homeowners_insurance_rate_percent,
            purchase_price,
            monthly_rent,
            tenant_rent,
            yearly_income,
            purchase_closing_cost_percent,
            sale_closing_cost_percent,
            annual_appreciation_percent,
            scenario_name,
            hoa,
            rent_control_percent,
            index_fund_annual_return_percent
    ):
        self.interest_rate_percent = Decimal(interest_rate_percent)
        self.interest_rate = self.interest_rate_percent / 100
        assert loan_term_years % 1 == 0, 'loan_term_years must be an integer'
        self.loan_term_years = int(loan_term_years)
        self.loan_term_months = self.loan_term_years * c.MONTHS_PER_YEAR
        self.purchase_price = DollarDecimal(purchase_price)
        self.down_payment = DollarDecimal(down_payment_amount or (self.purchase_price * down_payment_percent / 100))
        self.down_payment_percent = down_payment_percent or float(self.down_payment / self.purchase_price * 100)
        self.loan_amount = DollarDecimal(self.purchase_price - self.down_payment)
        self.federal_tax_rate_percent = federal_tax_rate_percent
        self.federal_tax_rate = Decimal(self.federal_tax_rate_percent) / 100
        self.state_tax_rate_percent = state_tax_rate_percent
        self.state_tax_rate = Decimal(self.state_tax_rate_percent) / 100
        self.property_tax_rate_percent = property_tax_rate_percent
        self.property_tax_rate = Decimal(self.property_tax_rate_percent) / 100
        self.homeowners_insurance_rate_percent = homeowners_insurance_rate_percent
        self.homeowners_insurance_rate = Decimal(self.homeowners_insurance_rate_percent) / 100
        self.yearly_income = DollarDecimal(yearly_income)
        self.initial_monthly_rent = DollarDecimal(monthly_rent)
        self.tenant_rent = DollarDecimal(tenant_rent) if tenant_rent else None
        self.hoa = DollarDecimal(hoa) if hoa is not None else None
        self.purchase_closing_cost_percent = Decimal(purchase_closing_cost_percent)
        self.purchase_closing_cost = DollarDecimal(self.purchase_price * (self.purchase_closing_cost_percent / 100))
        self.sale_closing_cost_percent = Decimal(sale_closing_cost_percent)
        self.sale_closing_cost = DollarDecimal(self.sale_closing_cost_percent * purchase_price)
        self.yearly_property_tax = DollarDecimal(self.property_tax_rate * self.purchase_price)
        self.monthly_property_tax = DollarDecimal(self.yearly_property_tax / c.MONTHS_PER_YEAR)
        self.yearly_home_insurance = DollarDecimal(self.homeowners_insurance_rate * self.purchase_price)
        self.monthly_home_insurance = DollarDecimal(self.yearly_home_insurance / c.MONTHS_PER_YEAR)
        self.mortgage = Mortgage(
            interest_rate=self.interest_rate, loan_amount=self.loan_amount, loan_term_months=self.loan_term_months
        )
        self.tax_deduction_per_year = self.calculate_tax_deduction_per_year()
        self.annual_appreciation_percent = Decimal(annual_appreciation_percent)
        self.annual_appreciation_rate = self.annual_appreciation_percent / 100

        self._federal_tax_savings_per_year = self.calculate_tax_savings_per_year(
            self.federal_tax_rate, federal_taxes['standard_deduction']
        )
        self._state_tax_savings_per_year = self.calculate_tax_savings_per_year(
            self.state_tax_rate, state_taxes['standard_deduction']
        )
        self._yearly_appreciated_price = self.calculate_yearly_appreciated_price()
        self.rent_control_percent = rent_control_percent
        self.rent_control_rate = Decimal(rent_control_percent or 0) / 100
        self.index_fund_annual_return_percent = index_fund_annual_return_percent or 10
        self.index_fund_annual_return_rate = Decimal(index_fund_annual_return_percent) / 100
        self.scenario_name = scenario_name

    def describe(self):
        table = []
        table.append(['Purchase price', f'{self.purchase_price}'])
        table.append(['Down payment', f'{self.down_payment} ({self.down_payment_percent}%)'])
        table.append(['Interest rate', f'{self.interest_rate_percent}%'])
        table.append(['Loan amount', f'{self.loan_amount}'])
        table.append(['Loan term', f'{self.loan_term_years} years ({self.loan_term_months} months)'])
        table.append(['Yearly homeowners insurance',
                      f'{self.yearly_home_insurance} ({self.homeowners_insurance_rate_percent}%)'])
        table.append(['Yearly property tax', f'{self.yearly_property_tax} ({self.property_tax_rate_percent}%)'])
        table.append(['Purchase closing cost', f'{self.purchase_closing_cost} ({self.purchase_closing_cost_percent}%)'])
        if self.hoa is not None:
            table.append(['HOA', f'{self.hoa}'])
        table.append(['Monthly rent', f'{self.initial_monthly_rent}'])
        if self.tenant_rent is not None:
            table.append(['Tenant rent', f'{self.tenant_rent}'])
        table.append(['Annual appreciation', f'{self.annual_appreciation_percent}%'])
        table.append(['Index Fund Annual Return Rate', f'{self.index_fund_annual_return_percent}%'])

        print(tabulate(pd.DataFrame(table), showindex=False))
        print('\n')

    def calculate_tax_deduction_per_year(self):
        result = []
        property_tax = self.property_tax_rate * self.purchase_price
        for year_num, principal, interest, deductible_interest in self.mortgage.yearly_mortgage_schedule():
            deductible_property_tax = min(property_tax, 10000)
            total_deduction = deductible_property_tax + deductible_interest
            result.append(min(total_deduction, self.yearly_income))

        return result

    def calculate_tax_savings_per_year(self, tax_rate, standard_deduction):
        result = []
        for tax_deduction in self.tax_deduction_per_year:
            itemized_savings = tax_rate * tax_deduction
            standard_deduction_savings = tax_rate * standard_deduction
            if itemized_savings > standard_deduction_savings:
                itemized_savings -= standard_deduction_savings
            else:
                itemized_savings = 0

            result.append(DollarDecimal(itemized_savings))

        return result

    def federal_tax_savings(self, year):
        return self._federal_tax_savings_per_year[year - 1]

    def state_tax_savings(self, year):
        return self._state_tax_savings_per_year[year - 1]

    def principal_after_n_years(self, n):
        total_principal = Decimal(self.down_payment)
        for monthly_payment in self.monthly(years=n).generator():
            total_principal += monthly_payment['principal']

        return DollarDecimal(total_principal)

    def non_principal_cost_after_n_years(self, n):
        total_cost = Decimal(0)
        for monthly_payment in self.monthly(years=n).generator():
            total_cost += monthly_payment['total_with_savings_minus_principal']

        return DollarDecimal(total_cost)

    def calculate_yearly_appreciated_price(self):
        return [self.purchase_price] + [
            DollarDecimal(
                compound_interest(self.purchase_price, self.annual_appreciation_rate, year, 1)
            ) for year in rangei(1, self.loan_term_years)
        ]

    def appreciated_price(self, year):
        return self._yearly_appreciated_price[year - 1]

    def yearly_appreciation(self, year):
        return self.appreciated_price(year + 1) - self.appreciated_price(year)

    def monthly_appreciation(self, year):
        return self.yearly_appreciation(year) / c.MONTHS_PER_YEAR

    def monthly(self, years=None, months=None, dollar_decimal_to_str=True):
        return MonthlyBreakdown(
            years=years, months=months, investment_breakdown=self, dollar_decimal_to_str=dollar_decimal_to_str
        )

    def yearly(self, years=None, dollar_decimal_to_str=True):
        return YearlyBreakdown(investment_breakdown=self, years=years, dollar_decimal_to_str=dollar_decimal_to_str)

    def rent(self, year):
        return compound_interest(self.initial_monthly_rent, self.rent_control_rate, year - 1, 1)
