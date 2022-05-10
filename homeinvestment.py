from decimal import Decimal

import pandas as pd
import yaml
from tabulate import tabulate

import constants as c
from decimaldollar import DecimalDollar
from decimalpercent import DecimalPercent
from helpers import rangei, compound_interest
from monthlysummary import MonthlySummary
from mortgage import Mortgage
from yearlysummary import YearlySummary

STATE_TAXES = yaml.safe_load(open('./taxes/state/ca.yaml'))
FEDERAL_TAXES = yaml.safe_load(open('./taxes/federal.yaml'))
MAX_DEDUCTIBLE_PROPERTY_TAX = DecimalDollar(FEDERAL_TAXES['property_tax_limit'])


class HomeInvestment(object):
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
            rent,
            rent_control_percent,
            tenant_rent,
            tenant_rent_control_percent,
            vacancy_rate_percent,
            yearly_income,
            purchase_closing_cost_percent,
            sale_closing_cost_percent,
            annual_appreciation_percent,
            scenario_name,
            hoa,
            index_fund_annual_return_percent
    ):
        self.interest_rate_percent = DecimalPercent(interest_rate_percent)
        self.interest_rate = self.interest_rate_percent / 100
        assert loan_term_years % 1 == 0, 'loan_term_years must be an integer'
        self.loan_term_years = int(loan_term_years)
        self.loan_term_months = self.loan_term_years * c.MONTHS_PER_YEAR
        self.purchase_price = DecimalDollar(purchase_price)
        self.down_payment = DecimalDollar(down_payment_amount or (self.purchase_price * down_payment_percent / 100))
        self.down_payment_percent = DecimalPercent(
            down_payment_percent or float(self.down_payment / self.purchase_price * 100)
        )
        self.loan_amount = DecimalDollar(self.purchase_price - self.down_payment)
        self.federal_tax_rate_percent = DecimalPercent(federal_tax_rate_percent)
        self.federal_tax_rate = Decimal(self.federal_tax_rate_percent) / 100
        self.state_tax_rate_percent = DecimalPercent(state_tax_rate_percent)
        self.state_tax_rate = Decimal(self.state_tax_rate_percent) / 100
        self.property_tax_rate_percent = DecimalPercent(property_tax_rate_percent)
        self.property_tax_rate = Decimal(self.property_tax_rate_percent) / 100
        self.homeowners_insurance_rate_percent = DecimalPercent(homeowners_insurance_rate_percent)
        self.homeowners_insurance_rate = Decimal(self.homeowners_insurance_rate_percent) / 100
        self.yearly_income = DecimalDollar(yearly_income)
        self.initial_rent = DecimalDollar(rent)
        self.rent_control_percent = DecimalPercent(rent_control_percent or 0)
        self.rent_control_rate = Decimal(rent_control_percent) / 100
        self.initial_tenant_rent = DecimalDollar(tenant_rent or 0)
        self.tenant_rent_control_percent = DecimalPercent(tenant_rent_control_percent or 0)
        self.tenant_rent_control_rate = self.tenant_rent_control_percent / 100
        self.vacancy_rate_percent = DecimalPercent(vacancy_rate_percent or 0)
        self.vacancy_rate = Decimal(self.vacancy_rate_percent / 100)
        self.hoa = DecimalDollar(hoa or 0)
        self.purchase_closing_cost_percent = DecimalPercent(purchase_closing_cost_percent)
        self.purchase_closing_cost_rate = Decimal(self.purchase_closing_cost_percent) / 100
        self.purchase_closing_cost = DecimalDollar(self.purchase_price * self.purchase_closing_cost_rate)
        self.sale_closing_cost_percent = DecimalPercent(sale_closing_cost_percent)
        self.sale_closing_cost_rate = Decimal(sale_closing_cost_percent / 100)
        self.sale_closing_cost = DecimalDollar(self.sale_closing_cost_percent * purchase_price)
        self.property_tax_yearly = DecimalDollar(self.property_tax_rate * self.purchase_price)
        self.property_tax = DecimalDollar(self.property_tax_yearly / c.MONTHS_PER_YEAR)
        self.home_insurance_yearly = DecimalDollar(self.homeowners_insurance_rate * self.purchase_price)
        self.home_insurance = DecimalDollar(self.home_insurance_yearly / c.MONTHS_PER_YEAR)
        self.mortgage = Mortgage(
            interest_rate=self.interest_rate, loan_amount=self.loan_amount, loan_term_months=self.loan_term_months
        )
        self.tax_deduction_per_year = self.calculate_tax_deduction_per_year()
        self.annual_appreciation_percent = DecimalPercent(annual_appreciation_percent)
        self.annual_appreciation_rate = self.annual_appreciation_percent / 100

        self._federal_tax_savings_per_year = self.calculate_tax_savings_per_year(
            self.federal_tax_rate, FEDERAL_TAXES['standard_deduction']
        )
        self._state_tax_savings_per_year = self.calculate_tax_savings_per_year(
            self.state_tax_rate, STATE_TAXES['standard_deduction']
        )
        self._yearly_appreciated_price = self.calculate_yearly_appreciated_price()
        self.index_fund_annual_return_percent = DecimalPercent(index_fund_annual_return_percent or 10)
        self.index_fund_annual_return_rate = Decimal(index_fund_annual_return_percent) / 100
        self.initial_cost = self.down_payment + self.purchase_closing_cost
        self.scenario_name = scenario_name

    def describe(self):
        table = []
        table.append(['Purchase price', f'{self.purchase_price}'])
        table.append(['Down payment', f'{self.down_payment} ({self.down_payment_percent})'])
        table.append(['Interest rate', f'{self.interest_rate_percent}'])
        table.append(['Loan amount', f'{self.loan_amount}'])
        table.append(['Loan term', f'{self.loan_term_years} years ({self.loan_term_months} months)'])
        table.append(['Yearly homeowners insurance',
                      f'{self.home_insurance_yearly} ({self.homeowners_insurance_rate_percent})'])
        table.append(['Yearly property tax', f'{self.property_tax_yearly} ({self.property_tax_rate_percent})'])
        table.append(['Purchase closing cost', f'{self.purchase_closing_cost} ({self.purchase_closing_cost_percent})'])
        table.append(['HOA', f'{self.hoa}'])
        table.append(['Monthly rent', f'{self.initial_rent}'])
        table.append(['Rent control', f'{self.rent_control_percent}'])
        table.append(['Tenant rent', f'{self.initial_tenant_rent}'])
        table.append(['Tenant rent control', f'{self.tenant_rent_control_percent}'])
        table.append(['Tenant vacancy rate', f'{self.vacancy_rate_percent}'])
        table.append(['Annual appreciation', f'{self.annual_appreciation_percent}'])
        table.append(['Index Fund Annual Return Rate', f'{self.index_fund_annual_return_percent}'])

        print(tabulate(pd.DataFrame(table), showindex=False))
        print('\n')

    def calculate_tax_deduction_per_year(self):
        result = []
        property_tax = self.property_tax_rate * self.purchase_price
        for year_num, principle, interest, deductible_interest in self.mortgage.yearly_mortgage_schedule():
            deductible_property_tax = min(property_tax, MAX_DEDUCTIBLE_PROPERTY_TAX)
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

            result.append(DecimalDollar(itemized_savings))

        return result

    def federal_tax_savings(self, year):
        return self._federal_tax_savings_per_year[year - 1]

    def state_tax_savings(self, year):
        return self._state_tax_savings_per_year[year - 1]

    def calculate_yearly_appreciated_price(self):
        return [self.purchase_price] + [
            DecimalDollar(
                compound_interest(self.purchase_price, self.annual_appreciation_rate, year, 1)
            ) for year in rangei(1, self.loan_term_years)
        ]

    def appreciated_price(self, year):
        return self._yearly_appreciated_price[year - 1]

    def yearly_appreciation(self, year):
        return self.appreciated_price(year + 1) - self.appreciated_price(year)

    def monthly_appreciation(self, year):
        return self.yearly_appreciation(year) / c.MONTHS_PER_YEAR

    def monthly(self, years=None, months=None):
        return MonthlySummary(years=years, months=months, home_investment=self)

    def yearly(self, years=None):
        return YearlySummary(home_investment=self, years=years)

    def rent(self, year):
        return compound_interest(self.initial_rent, self.rent_control_rate, year - 1, 1)

    def tenant_rent(self, year):
        return compound_interest(self.initial_tenant_rent, self.tenant_rent_control_rate, year - 1, 1)

    def vacancy_cost(self, year):
        return self.tenant_rent(year) * self.vacancy_rate
