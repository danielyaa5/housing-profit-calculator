import functools
from decimal import Decimal

from src.decimal.percent import Percent


class Rate(Decimal):
    def __new__(cls, *args, percent=None, **kwargs):
        if percent is not None:
            return Rate(percent / 100)
        return super().__new__(cls, *args, **kwargs)

    @functools.cached_property
    def percent(self):
        return Percent(self * 100)

    def __sub__(self, other):
        return Rate(super().__sub__(other))

    def __add__(self, other):
        return Rate(super().__add__(other))

    def __mul__(self, other):
        return Rate(super().__mul__(other))

    def __truediv__(self, other):
        return Rate(super().__truediv__(other))

    def __floordiv__(self, other):
        return Rate(super().__floordiv__(other))

    def __mod__(self, other):
        return Rate(super().__mod__(other))

    def __neg__(self):
        return Rate(super().__neg__())

    def __pos__(self):
        return Rate(super().__pos__())

    def __abs__(self):
        return Rate(super().__abs__())

    def __round__(self, *args, **kwargs):
        return Rate(super().__round__(*args, **kwargs))

    def __trunc__(self):
        return Rate(super().__trunc__())

    def __floor__(self):
        return Rate(super().__floor__())

    def __ceil__(self):
        return Rate(super().__ceil__())

    def __pow__(self, *args, **kwargs):
        return Rate(super().__pow__(*args, **kwargs))

    def __radd__(self, other):
        return Rate(super().__radd__(other))
