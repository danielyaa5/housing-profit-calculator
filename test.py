from src.helpers import folder_del_contents, rel, compound_interest
from src.homeinvestment import HomeInvestment
from src.income import income
from src.mortgage import mortgage
from src.operatingexpenses import operating_expenses
from src.purchase import purchase
from src.sale import sale
from src.taxes import taxes


def test_home_investment_condo():
    return HomeInvestment(
        scenario_name='home_investment_condo',
        purchase=purchase(
            price=800 * 1000,
            down_payment=None,
            down_payment_percent=20,
            closing_cost_percent=2
        ),
        mortgage=mortgage(
            interest_rate_percent=4.75,
            loan_term_years=30
        ),
        taxes=taxes(
            property_tax_percent=1.25,
            property_tax_annual_increase_percent=2,
            federal_tax_rate_percent=35,
            state_tax_rate_percent=11.3,
            yearly_income=500 * 1000,
        ),
        operating_expenses=operating_expenses(
            hoi_percent=0.22,
            hoi_annual_increase_percent=2,
            hoa=325,
            hoa_annual_increase_percent=2,
            maintenance_percent=0.25,
            maintenance_annual_increase_percent=2,
            other_percent=None,
            other_annual_increase_percent=None
        ),
        income=income(
            rent=4000,
            rent_annual_increase_percent=3,
            tenant_rent=None,
            tenant_rent_annual_increase_percent=None,
            vacancy_percent=None,
            management_fee_percent=None,
        ),
        sale=sale(
            closing_cost_percent=8,
            annual_appreciation_percent=3,
        ),
        index_fund_annual_return_percent=8,
    )


def test_home_investment_low_interest_house():
    return HomeInvestment(
        scenario_name='home_investment_low_interest_house',
        purchase=purchase(
            price=900 * 1000,
            down_payment=None,
            down_payment_percent=20,
            closing_cost_percent=2
        ),
        mortgage=mortgage(
            interest_rate_percent=3.25,
            loan_term_years=30
        ),
        taxes=taxes(
            property_tax_percent=1.25,
            property_tax_annual_increase_percent=2,
            federal_tax_rate_percent=35,
            state_tax_rate_percent=11.3,
            yearly_income=500 * 1000,
        ),
        operating_expenses=operating_expenses(
            hoi_percent=0.22,
            hoi_annual_increase_percent=2,
            hoa=None,
            hoa_annual_increase_percent=None,
            maintenance_percent=1,
            maintenance_annual_increase_percent=2,
            other_percent=None,
            other_annual_increase_percent=None
        ),
        income=income(
            rent=1650,
            rent_annual_increase_percent=3,
            tenant_rent=1600,
            tenant_rent_annual_increase_percent=None,
            vacancy_percent=None,
            management_fee_percent=None,
        ),
        sale=sale(
            closing_cost_percent=8,
            annual_appreciation_percent=5,
        ),
        index_fund_annual_return_percent=10,
    )


def test_home_investment_low_interest_house_fully_rented():
    return HomeInvestment(
        scenario_name='home_investment_low_interest_house_fully_rented',
        purchase=purchase(
            price=850 * 1000,
            down_payment=None,
            down_payment_percent=20,
            closing_cost_percent=2
        ),
        mortgage=mortgage(
            interest_rate_percent=3.25,
            loan_term_years=30
        ),
        taxes=taxes(
            property_tax_percent=1.25,
            property_tax_annual_increase_percent=2,
            federal_tax_rate_percent=35,
            state_tax_rate_percent=11.3,
            yearly_income=500 * 1000,
        ),
        operating_expenses=operating_expenses(
            hoi_percent=0.22,
            hoi_annual_increase_percent=2,
            hoa=None,
            hoa_annual_increase_percent=None,
            maintenance_percent=1,
            maintenance_annual_increase_percent=2,
            other_percent=None,
            other_annual_increase_percent=None
        ),
        income=income(
            rent=None,
            rent_annual_increase_percent=None,
            tenant_rent=4500,
            tenant_rent_annual_increase_percent=3,
            vacancy_percent=5,
            management_fee_percent=8,
        ),
        sale=sale(
            closing_cost_percent=8,
            annual_appreciation_percent=5,
        ),
        index_fund_annual_return_percent=9,
    )


if __name__ == '__main__':
    folder_del_contents(rel('./output'))
    print('testing...')
    hi = test_home_investment_low_interest_house_fully_rented()
    hi.describe()
    hi.breakdown.yearly.csv_income()
    hi.breakdown.yearly.csv_operating_cost()
    hi.breakdown.yearly.csv_cashflow()
    hi.breakdown.yearly.csv_investment()
    hi.breakdown.monthly.csv_income()
    hi.breakdown.monthly.csv_operating_cost()
    hi.breakdown.monthly.csv_cashflow()
    hi.breakdown.monthly.csv_investment()
