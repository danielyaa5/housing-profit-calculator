from decimal import Decimal


def range_is_last(start, end):
    for i in range(start, end):
        yield i == end, i


def rangei(start, end):
    return range(start, end + 1)


def rangei_is_last(start, end):
    return range_is_last(start, end + 1)


def get_decimal(dct, key, default=None):
    if key in dct:
        return Decimal(dct[key])
    return default


def compound_interest(principal, interest_rate, years, number):
    # calculate total amount
    amount = principal * pow(1 + (interest_rate / number), number * years)
    return amount
