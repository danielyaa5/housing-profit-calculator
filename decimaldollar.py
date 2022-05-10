from decimal import Decimal

import constants as c


class DecimalDollar(Decimal):
    def __format__(self, *args, **kwargs):
        f = super().quantize(c.TENTH_PLACE_QUANTIZE).__float__()
        is_neg = f < 0
        result = '$' + format(abs(f), ',')
        if is_neg:
            result = '-' + result
        no_hundreds_place = len(result.split('.')[1]) == 1
        if no_hundreds_place:
            result += '0'
        return result

    def quantize(self, *args, **kwargs):
        return DecimalDollar(super().quantize(*args, **kwargs))

    def __sub__(self, other):
        return DecimalDollar(super().__sub__(other))

    def __add__(self, other):
        return DecimalDollar(super().__add__(other))

    def __mul__(self, other):
        return DecimalDollar(super().__mul__(other))

    def __truediv__(self, other):
        return DecimalDollar(super().__truediv__(other))

    def __floordiv__(self, other):
        return DecimalDollar(super().__floordiv__(other))

    def __mod__(self, other):
        return DecimalDollar(super().__mod__(other))

    def __neg__(self):
        return DecimalDollar(super().__neg__())

    def __pos__(self):
        return DecimalDollar(super().__pos__())

    def __abs__(self):
        return DecimalDollar(super().__abs__())

    def __round__(self, *args, **kwargs):
        return DecimalDollar(super().__round__(*args, **kwargs))

    def __trunc__(self):
        return DecimalDollar(super().__trunc__())

    def __floor__(self):
        return DecimalDollar(super().__floor__())

    def __ceil__(self):
        return DecimalDollar(super().__ceil__())

    def __pow__(self, *args, **kwargs):
        return DecimalDollar(super().__pow__(*args, **kwargs))

    def __radd__(self, other):
        return DecimalDollar(super().__radd__(other))
