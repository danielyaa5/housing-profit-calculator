import inspect
import operator
import os
import shutil
from decimal import Decimal
from functools import reduce

import yaml


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


def compound_interest(principle, rate, years, number):
    # calculate total amount
    amount = principle * pow(1 + (rate / number), number * years)
    return amount


def compound_yearly(principle, rate, years):
    return compound_interest(principle, rate, years, 1)


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


def rel(*path):
    caller_filepath = inspect.stack()[1].filename
    caller_dirname = os.path.dirname(caller_filepath)
    return os.path.realpath(os.path.join(caller_dirname, *path))


def yaml_safe_load(path):
    with open(path) as f:
        return yaml.safe_load(f)
