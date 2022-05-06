import decimal

DOLLAR_QUANTIZE = decimal.Decimal('.01')


def rangei(start, end):
    return range(start, end + 1)


def get_decimal(dct, key, default=None):
    if key in dct:
        return decimal.Decimal(dct[key])
    return default


def dollar(f, round=decimal.ROUND_CEILING):
    """
    This function rounds the passed float to 2 decimal places.
    """
    if not isinstance(f, decimal.Decimal):
        f = decimal.Decimal(str(f))
    return f.quantize(DOLLAR_QUANTIZE, rounding=round)


def compound_interest(principal, interest_rate, years, number):
    # calculate total amount
    amount = principal * pow(1 + (interest_rate / number), number * years)
    return amount
