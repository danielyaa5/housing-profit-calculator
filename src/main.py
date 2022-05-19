import argparse
import os
import sys


def _parse_args():
    # Creates and returns the ArgumentParser object
    parser = argparse.ArgumentParser(description='Calculate profitability of purchasing a house')
    parser.add_argument(
        '-i', '--input',
        help='Path to a yaml file describing the input parameters, such as house price and interest_rate rate',
        required=True,
        type=os.path.abspath
    )
    parser.add_argument(
        '-d', '--delete-output',
        help='Delete everything in the output directory',
        action='store_true'
    )
    return parser.parse_args(sys.argv[1:])


# def _load_house_params(house_params_path):
#     assert os.path.exists(house_params_path), 'Input path does not exist'
#
#     house_params = yaml.safe_load(open(house_params_path))
#     return HomeInvestment(
#         interest_rate=house_params['interest_rate'],
#         down_payment=house_params.get('down_payment'),
#         down_payment_percent=house_params.get('down_payment_percent'),
#         loan_term_years=house_params['loan_term_years'],
#         federal_tax_rate=house_params['federal_tax_rate'],
#         state_tax_rate=house_params['state_tax_rate'],
#         property_tax_rate=house_params['property_tax_rate'],
#         hoi_rate=house_params['hoi_rate'],
#         purchase_price=house_params['price'],
#         yearly_income=house_params['yearly_income'],
#         rent=house_params.get('rent'),
#         rent_annual_increase_rate=house_params.get('rent_annual_increase_rate'),
#         vacancy_percent=house_params.get('vacancy_percent'),
#         tenant_rent=house_params.get('tenant_rent'),
#         tenant_rent_control_percent=house_params.get('tenant_rent_control_percent'),
#         hoa=house_params.get('hoa'),
#         purchase_closing_cost_percent=house_params['purchase_closing_cost_percent'],
#         closing_cost_percent=house_params.get('closing_cost_percent'),
#         annual_appreciation_percent=house_params.get('annual_appreciation_percent'),
#         index_fund_annual_return_percent=house_params.get('index_fund_annual_return_percent'),
#         scenario_name=pathlib.Path(house_params_path).stem,
#         maintenance_rate=house_params.get('maintenance_rate'),
#     )


def main(home_investment, delete_output):
    pass


if __name__ == '__main__':
    args = _parse_args()
