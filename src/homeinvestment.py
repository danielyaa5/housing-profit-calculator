import pandas as pd
from tabulate import tabulate

from src.breakdown.investmentbreakdown import InvestmentBreakdown
from src.decimal.rate import Rate
from src.income import IncomeFactoryType
from src.mortgage import MortgageFactoryType
from src.operatingexpenses import OperatingExpensesFactoryType
from src.purchase import PurchaseFactoryType
from src.sale import SaleFactoryType
from src.taxes import TaxesFactoryType


class HomeInvestment(object):
    def __init__(
            self,
            scenario_name,
            purchase: PurchaseFactoryType,
            mortgage: MortgageFactoryType,
            taxes: TaxesFactoryType,
            operating_expenses: OperatingExpensesFactoryType,
            income: IncomeFactoryType,
            sale: SaleFactoryType,

            # Index fund
            index_fund_annual_return_percent,
    ):
        self.scenario_name = scenario_name
        self.purchase = purchase()
        self.mortgage = mortgage(self.purchase)
        self.taxes = taxes(self.mortgage, self.purchase)
        self.income = income(self.taxes)
        self.operating_expenses = operating_expenses(self.purchase, self.income, self.taxes)
        self.sale = sale(self.purchase)
        self.index_fund_annual_return_rate = Rate(percent=index_fund_annual_return_percent or 10)
        self.breakdown = InvestmentBreakdown(self)
        self._describe_tables = _create_describe_tables(self)

    def describe(self):
        def tabulate_describe(description):
            print(f'\n{description["header"]}')
            df = pd.DataFrame(description['table'])
            if description['columns'] is None:
                return tabulate(df, tablefmt='fancy_grid', showindex=False)

            return tabulate(df, tablefmt='fancy_grid', headers=description['columns'], showindex=False)

        print('\n====================================')
        print('\n==== Home Investment Parameters ====')
        print('\n====================================')
        for table in self._describe_tables:
            print(tabulate_describe(table))

        print('\n')


def _create_describe_tables(i: HomeInvestment):
    expenses = i.operating_expenses
    return [
        dict(
            header='Purchase Params',
            columns=None,
            table=[
                ['Purchase Price', f'{i.purchase.price}'],
                ['Down Payment', f'{i.purchase.down_payment} [{i.purchase.down_payment_percent}]'],
                ['Closing Cost', f'{i.purchase.closing_cost} [{i.purchase.closing_cost_rate.percent}]'],
            ]
        ),
        dict(
            header='Mortgage Params',
            columns=None,
            table=[
                ['Loan Amount', f'{i.mortgage.loan_amount}'],
                ['Interest Rate', f'{i.mortgage.interest_rate.percent}'],
                ['Loan Term', f'{i.mortgage.loan_term_years} years ({i.mortgage.loan_term_months} months)'],
            ]
        ),
        dict(
            header='Operating Expenses Params',
            columns=['', 'Initial Monthly', 'Annual Increase'],
            table=[
                ['Property Tax', f'{expenses.property_tax[1]} [{expenses.property_tax_rate.percent}]',
                 f'{i.taxes.property_tax_annual_increase_rate.percent}'],
                ['HOI', f'{expenses.hoi[1]} [{expenses.hoi_rate.percent}]',
                 f'{expenses.hoi_annual_increase_rate.percent}'],
                ['HOA', f'{expenses.hoa[1]}', f'{expenses.hoa_annual_increase_rate.percent}'],
                ['Maintenance', f'{expenses.maintenance[1]} [{expenses.maintenance_rate.percent}]',
                 f'{expenses.maintenance_annual_increase_rate.percent}'],
                ['Other Costs', f'{expenses.other[1]} [{expenses.other_rate.percent}]',
                 f'{expenses.other_annual_increase_rate.percent}'],
            ]
        ),
        dict(
            header='Income Params',
            columns=['', 'Initial Monthly', 'Annual Increase'],
            table=[
                ['Rent', f'{i.income.rent[1]}', f'{i.income.rent_annual_increase_rate.percent}'],
                ['Tenant Rent', f'{i.income.tenant_rent[1]}', f'{i.income.tenant_rent_annual_increase_rate.percent}'],
                ['Vacancy', f'{expenses.vacancy(month=0)} [{i.income.vacancy_rate.percent}]', ''],
                ['Management Fee', f'{expenses.management_fee(month=0)} [{i.income.management_fee_rate.percent}]', ''],
            ]
        ),
        dict(
            header='Taxes Params',
            columns=None,
            table=[
                ['Yearly Income', f'{i.taxes.yearly_income}'],
                ['Federal Tax Rate', f'{i.taxes.federal_tax_rate.percent}'],
                ['State Tax Rate', f'{i.taxes.state_tax_rate.percent}'],
                ['Federal Standard Deduction', f'{i.taxes.federal_standard_deduction}'],
                ['State Standard Deduction', f'{i.taxes.state_standard_deduction}'],
            ]
        ),
        dict(
            header='Sale Params',
            columns=None,
            table=[
                ['Closing Cost', f'{i.sale.closing_cost_rate.percent}'],
                ['Annual Appreciation', f'{i.sale.annual_appreciation_rate.percent}'],
            ]
        ),
        dict(
            header='Index Fund Params',
            columns=None,
            table=[
                ['Annual Return', f'{i.index_fund_annual_return_rate.percent}'],
            ]
        )
    ]
