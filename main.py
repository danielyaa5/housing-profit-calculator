import argparse
import decimal
import os
import sys

import pandas as pd
import yaml
from tabulate import tabulate

from helpers import get_decimal, compound_interest
from payments import Payments


def create_arg_parser():
    # Creates and returns the ArgumentParser object

    parser = argparse.ArgumentParser(description='Calculate profitability of purchasing a house')
    parser.add_argument(
        '-i', '--input',
        help='Path to a yaml file describing the input parameters, such as house price and interest rate',
        required=True,
        type=os.path.abspath
    )
    return parser


def main(house_params):
    price = decimal.Decimal(house_params['price'])
    loan_term_years = int(house_params['loan_term_years'])
    interest_rate_percent = decimal.Decimal(house_params['interest_rate_percent'])
    state_tax_rate_percent = decimal.Decimal(house_params['state_tax_rate_percent'])
    federal_tax_rate_percent = decimal.Decimal(house_params['federal_tax_rate_percent'])
    property_tax_rate_percent = decimal.Decimal(house_params['property_tax_rate_percent'])
    homeowners_insurance_rate_percent = decimal.Decimal(house_params['homeowners_insurance_rate_percent'])
    yearly_income = decimal.Decimal(house_params['yearly_income'])
    monthly_rent = decimal.Decimal(house_params['monthly_rent'])
    tenant_rent = decimal.Decimal(house_params.get('tenant_rent', 0))
    purchase_closing_cost_percent = decimal.Decimal(house_params['purchase_closing_cost_percent'])
    down_payment_percent = get_decimal(house_params, 'down_payment_percent')
    down_payment_amount = get_decimal(house_params, 'down_payment_amount') or price * (down_payment_percent / 100)
    earnings_after_years = house_params.get('earnings_after_years')
    annual_appreciation = get_decimal(house_params, 'annual_appreciation')
    sale_closing_cost_percent = get_decimal(house_params, 'sale_closing_cost_percent')

    loan_amount = price - down_payment_amount
    interest_rate = interest_rate_percent / 100
    loan_term_months = loan_term_years * 12
    federal_tax_rate = federal_tax_rate_percent / 100
    state_tax_rate = state_tax_rate_percent / 100
    property_tax_rate = property_tax_rate_percent / 100
    homeowners_insurance_rate = homeowners_insurance_rate_percent / 100
    purchase_closing_cost = price * (purchase_closing_cost_percent / 100)

    print(f'Calculating monthly mortgage payments for:')
    print(f'Price: ${price}')
    print(f'Down payment: ${down_payment_amount}')
    print(f'Loan amount: ${loan_amount}')
    print(f'Loan term: {loan_term_years} years')
    print(f'Interest rate: {interest_rate_percent}%')
    print(f'Purchase closing cost: ${purchase_closing_cost}')
    print('\n')

    payments = Payments(
        interest_rate=interest_rate,
        loan_amount=loan_amount,
        loan_term_months=loan_term_months,
        federal_tax_rate=federal_tax_rate,
        state_tax_rate=state_tax_rate,
        property_tax_rate=property_tax_rate,
        homeowners_insurance_rate=homeowners_insurance_rate,
        purchase_price=price,
        yearly_income=yearly_income,
        monthly_rent=monthly_rent,
        tenant_rent=tenant_rent,
    )
    print(tabulate(pd.DataFrame(payments.monthly_payment_schedule(years=5)), headers='keys', showindex=False))

    if annual_appreciation:
        print(f'\nCalculate return after {earnings_after_years} years')
        sale_closing_cost_percent = house_params['sale_closing_cost_percent']
        total_principle = payments.principal_after_n_years(earnings_after_years)
        print(f'Principal: ${total_principle}')
        total_non_principal_cost = payments.non_principal_cost_after_n_years(earnings_after_years)
        print(f'Total non principal cost: ${total_non_principal_cost}')
        house_value_after_years = compound_interest(price, annual_appreciation, earnings_after_years, 1)
        print(f'House value: ${house_value_after_years}')
        sale_closing_sale_cost = house_value_after_years * sale_closing_cost_percent / 100
        print(f'Sale closing cost: ${sale_closing_sale_cost}')
        total_cost = purchase_closing_cost + total_non_principal_cost + sale_closing_sale_cost
        print(f'Total cost: ${total_cost}')
        sale_profit = house_value_after_years - price
        print(f'Sale profit: ${sale_profit}')
        profit = sale_profit - total_cost
        print(f'Profit: ${profit}')


if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    assert os.path.exists(parsed_args.input), 'Input directory does not exist'
    # Parse yaml file with input parameters
    main(yaml.safe_load(open(parsed_args.input)))
