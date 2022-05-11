import operator
import os
import shutil
from decimal import Decimal
from functools import reduce


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


def compound_interest(principle, interest_rate, years, number):
    # calculate total amount
    amount = principle * pow(1 + (interest_rate / number), number * years)
    return amount


def sub(iterable):
    return reduce(operator.__sub__, iterable)


def sum_reduce(f, iterable):
    return reduce(operator.__add__, map(f, iterable))


def folder_del_contents(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
