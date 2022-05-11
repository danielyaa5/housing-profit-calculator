import functools
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
            index_fund_annual_return_percent,
            maintenance_fee_percent,
    ):
        self.scenario_name = scenario_name

        # Loan
        assert loan_term_years % 1 == 0, 'loan_term_years must be a whole number'
        self.interest_rate_percent = DecimalPercent(interest_rate_percent)
        self.interest_rate = self.interest_rate_percent / 100
        self.loan_term_years = int(loan_term_years)
        self.loan_term_months = self.loan_term_years * c.MONTHS_PER_YEAR
        self.purchase_price = DecimalDollar(purchase_price)
        self.down_payment = DecimalDollar(down_payment_amount or (self.purchase_price * down_payment_percent / 100))
        self.down_payment_percent = DecimalPercent(
            down_payment_percent or float(self.down_payment / self.purchase_price * 100)
        )
        self.loan_amount = DecimalDollar(self.purchase_price - self.down_payment)
        self.mortgage = Mortgage(
            interest_rate=self.interest_rate,
            loan_amount=self.loan_amount,
            loan_term_months=self.loan_term_months
        )

        # ======================
        # = Positive Cash Flow =
        # ======================

        # Taxes
        self.federal_tax_rate_percent = DecimalPercent(federal_tax_rate_percent)
        self.federal_tax_rate = Decimal(self.federal_tax_rate_percent) / 100
        self.state_tax_rate_percent = DecimalPercent(state_tax_rate_percent)
        self.state_tax_rate = Decimal(self.state_tax_rate_percent) / 100
        self.property_tax_rate_percent = DecimalPercent(property_tax_rate_percent)
        self.property_tax_rate = Decimal(self.property_tax_rate_percent) / 100
        self.yearly_income = DecimalDollar(yearly_income)
        self.tax_deduction_per_year = self._calculate_tax_deduction_per_year()
        self.federal_standard_deduction = FEDERAL_TAXES['standard_deduction']
        self.state_standard_deduction = STATE_TAXES['standard_deduction']

        # Rent
        self.initial_rent = DecimalDollar(rent)
        self.rent_control_percent = DecimalPercent(rent_control_percent or 0)
        self.rent_control_rate = Decimal(rent_control_percent) / 100
        self.initial_tenant_rent = DecimalDollar(tenant_rent or 0)
        self.tenant_rent_control_percent = DecimalPercent(tenant_rent_control_percent or 0)
        self.tenant_rent_control_rate = self.tenant_rent_control_percent / 100

        # ======================
        # = Negative Cash Flow =
        # ======================

        # Recurring Costs
        self.homeowners_insurance_rate_percent = DecimalPercent(homeowners_insurance_rate_percent)
        self.homeowners_insurance_rate = Decimal(self.homeowners_insurance_rate_percent) / 100
        self.vacancy_rate_percent = DecimalPercent(vacancy_rate_percent or 0)
        self.vacancy_rate = Decimal(self.vacancy_rate_percent / 100)
        self.hoa = DecimalDollar(hoa or 0)
        self.maintenance_fee_percent = DecimalPercent(maintenance_fee_percent or 0)
        self.maintenance_fee_rate = Decimal(self.maintenance_fee_percent) / 100
        self.maintenance_fee_yearly = DecimalDollar(self.maintenance_fee_rate * self.purchase_price)
        self.maintenance_fee = self.maintenance_fee_yearly / c.MONTHS_PER_YEAR
        self.property_tax_yearly = DecimalDollar(self.property_tax_rate * self.purchase_price)
        self.property_tax = DecimalDollar(self.property_tax_yearly / c.MONTHS_PER_YEAR)
        self.hoi_yearly = DecimalDollar(self.homeowners_insurance_rate * self.purchase_price)
        self.hoi = DecimalDollar(self.hoi_yearly / c.MONTHS_PER_YEAR)

        # Onetime Costs
        self.purchase_closing_cost_percent = DecimalPercent(purchase_closing_cost_percent)
        self.purchase_closing_cost_rate = Decimal(self.purchase_closing_cost_percent) / 100
        self.purchase_closing_cost = DecimalDollar(self.purchase_price * self.purchase_closing_cost_rate)
        self.sale_closing_cost_percent = DecimalPercent(sale_closing_cost_percent)
        self.sale_closing_cost_rate = Decimal(sale_closing_cost_percent / 100)
        self.sale_closing_cost = DecimalDollar(self.sale_closing_cost_percent * purchase_price)
        self.initial_cost = self.down_payment + self.purchase_closing_cost

        # ====================
        # = Investment Value =
        # ====================

        self.annual_appreciation_percent = DecimalPercent(annual_appreciation_percent or 0)
        self.annual_appreciation_rate = self.annual_appreciation_percent / 100
        self.index_fund_annual_return_percent = DecimalPercent(index_fund_annual_return_percent or 10)
        self.index_fund_annual_return_rate = Decimal(index_fund_annual_return_percent) / 100

    def describe(self):
        table = []
        table.append(['Purchase price', f'{self.purchase_price}'])
        table.append(['Down payment', f'{self.down_payment} ({self.down_payment_percent})'])
        table.append(['Interest rate', f'{self.interest_rate_percent}'])
        table.append(['Loan amount', f'{self.loan_amount}'])
        table.append(['Loan term', f'{self.loan_term_years} years ({self.loan_term_months} months)'])
        table.append(['Yearly homeowners insurance',
                      f'{self.hoi_yearly} ({self.homeowners_insurance_rate_percent})'])
        table.append(['Yearly property tax', f'{self.property_tax_yearly} ({self.property_tax_rate_percent})'])
        table.append(['Purchase closing cost', f'{self.purchase_closing_cost} ({self.purchase_closing_cost_percent})'])
        table.append(['HOA', f'{self.hoa}'])
        table.append(['Monthly maintenance fee', f'{self.maintenance_fee}'])
        table.append(['Monthly rent', f'{self.initial_rent}'])
        table.append(['Rent control', f'{self.rent_control_percent}'])
        table.append(['Tenant rent', f'{self.initial_tenant_rent}'])
        table.append(['Tenant rent control', f'{self.tenant_rent_control_percent}'])
        table.append(['Tenant vacancy rate', f'{self.vacancy_rate_percent}'])
        table.append(['Annual appreciation', f'{self.annual_appreciation_percent}'])
        table.append(['Index Fund Annual Return Rate', f'{self.index_fund_annual_return_percent}'])

        print(tabulate(pd.DataFrame(table), showindex=False))
        print('\n')

    def _calculate_tax_deduction_per_year(self):
        result = []
        property_tax = self.property_tax_rate * self.purchase_price
        for year_num, principle, interest, deductible_interest in self.mortgage.yearly_mortgage_schedule():
            deductible_property_tax = min(property_tax, MAX_DEDUCTIBLE_PROPERTY_TAX)
            total_deduction = deductible_property_tax + deductible_interest
            result.append(min(total_deduction, self.yearly_income))

        return result

    def _calculate_tax_savings_per_year(self, tax_rate, standard_deduction):
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

    @functools.cached_property
    def federal_tax_savings_per_year(self):
        return self._calculate_tax_savings_per_year(self.federal_tax_rate, self.federal_standard_deduction)

    @functools.cached_property
    def state_tax_savings_per_year(self):
        return self._calculate_tax_savings_per_year(self.state_tax_rate, self.state_standard_deduction)

    def federal_tax_savings(self, year):
        return self.federal_tax_savings_per_year[year - 1]

    def state_tax_savings(self, year):
        return self.state_tax_savings_per_year[year - 1]

    @functools.cached_property
    def appreciated_price_per_year(self):
        return [self.purchase_price] + [
            DecimalDollar(
                compound_interest(self.purchase_price, self.annual_appreciation_rate, year, 1)
            ) for year in rangei(1, self.loan_term_years)
        ]

    def appreciated_price(self, year):
        return self.appreciated_price_per_year[year]

    def yearly_appreciation(self, year):
        return self.appreciated_price(year) - self.appreciated_price(year - 1)

    def monthly_appreciation(self, year):
        return self.yearly_appreciation(year) / c.MONTHS_PER_YEAR

    @functools.cache
    def monthly(self):
        return MonthlySummary(home_investment=self)

    @functools.cache
    def yearly(self):
        return YearlySummary(home_investment=self)

    def rent(self, year):
        return compound_interest(self.initial_rent, self.rent_control_rate, year - 1, 1)

    def tenant_rent(self, year):
        return compound_interest(self.initial_tenant_rent, self.tenant_rent_control_rate, year - 1, 1)

    def vacancy(self, year):
        return self.tenant_rent(year) * self.vacancy_rate
