import argparse
import os
import pathlib
import sys

import yaml

from helpers import folder_del_contents
from homeinvestment import HomeInvestment


def create_arg_parser():
    # Creates and returns the ArgumentParser object
    parser = argparse.ArgumentParser(description='Calculate profitability of purchasing a house')
    parser.add_argument(
        '-i', '--input',
        help='Path to a yaml file describing the input parameters, such as house price and interest rate',
        required=True,
        type=os.path.abspath
    )
    parser.add_argument(
        '-d', '--delete-output',
        help='Delete everything in the output directory',
        action='store_true'
    )
    return parser


def main(house_params_path):
    house_params = yaml.safe_load(open(house_params_path))
    investment_breakdown = HomeInvestment(
        interest_rate_percent=house_params['interest_rate_percent'],
        down_payment_amount=house_params.get('down_payment_amount'),
        down_payment_percent=house_params.get('down_payment_percent'),
        loan_term_years=house_params['loan_term_years'],
        federal_tax_rate_percent=house_params['federal_tax_rate_percent'],
        state_tax_rate_percent=house_params['state_tax_rate_percent'],
        property_tax_rate_percent=house_params['property_tax_rate_percent'],
        homeowners_insurance_rate_percent=house_params['homeowners_insurance_rate_percent'],
        purchase_price=house_params['purchase_price'],
        yearly_income=house_params['yearly_income'],
        rent=house_params.get('rent'),
        rent_control_percent=house_params.get('rent_control_percent'),
        vacancy_rate_percent=house_params.get('vacancy_rate_percent'),
        tenant_rent=house_params.get('tenant_rent'),
        tenant_rent_control_percent=house_params.get('tenant_rent_control_percent'),
        hoa=house_params.get('hoa'),
        purchase_closing_cost_percent=house_params['purchase_closing_cost_percent'],
        sale_closing_cost_percent=house_params.get('sale_closing_cost_percent'),
        annual_appreciation_percent=house_params.get('annual_appreciation_percent'),
        index_fund_annual_return_percent=house_params.get('index_fund_annual_return_percent'),
        scenario_name=pathlib.Path(house_params_path).stem,
        maintenance_fee_percent=house_params.get('maintenance_fee_percent'),
    )
    print('\n')
    print(f'Calculating monthly mortgage payments for:')
    print('\n')
    investment_breakdown.describe()

    investment_breakdown.monthly().csv()
    investment_breakdown.monthly().csv_cashflow_negative()
    investment_breakdown.monthly().csv_cashflow_positive()
    investment_breakdown.monthly().csv_investment()
    investment_breakdown.monthly().csv_investment_short()

    investment_breakdown.yearly().csv()
    investment_breakdown.yearly().csv_investment()
    investment_breakdown.yearly().csv_investment_short()


if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    assert os.path.exists(parsed_args.input), 'Input directory does not exist'

    # Delete everything in the output directory if the user requested it
    if parsed_args.delete_output:
        dirname = os.path.join(pathlib.Path(__file__).parent.resolve(), 'output')
        folder_del_contents(dirname)

    # Parse yaml file with input parameters
    main(parsed_args.input)
