import functools

from src.decimal.decimal import CustomDecimal


class Percent(CustomDecimal):
    def __format__(self, *args, **kwargs):
        return f'{self.to_str_2_digits()}%'

    @functools.cached_property
    def rate(self):
        from src.decimal.rate import Rate
        return Rate(self / 100)

    def quantize(self, *args, **kwargs):
        return Percent(super().quantize(*args, **kwargs))

    def __sub__(self, other):
        return Percent(super().__sub__(other))

    def __add__(self, other):
        return Percent(super().__add__(other))

    def __mul__(self, other):
        return Percent(super().__mul__(other))

    def __truediv__(self, other):
        return Percent(super().__truediv__(other))

    def __floordiv__(self, other):
        return Percent(super().__floordiv__(other))

    def __mod__(self, other):
        return Percent(super().__mod__(other))

    def __neg__(self):
        return Percent(super().__neg__())

    def __pos__(self):
        return Percent(super().__pos__())

    def __abs__(self):
        return Percent(super().__abs__())

    def __round__(self, *args, **kwargs):
        return Percent(super().__round__(*args, **kwargs))

    def __trunc__(self):
        return Percent(super().__trunc__())

    def __floor__(self):
        return Percent(super().__floor__())

    def __ceil__(self):
        return Percent(super().__ceil__())

    def __pow__(self, *args, **kwargs):
        return Percent(super().__pow__(*args, **kwargs))

    def __radd__(self, other):
        return Percent(super().__radd__(other))
