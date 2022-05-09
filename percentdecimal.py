from decimal import Decimal

import constants as c


class PercentDecimal(Decimal):
    def __format__(self, *args, **kwargs):
        f = super().quantize(c.TENTH_PLACE_QUANTIZE).__float__()
        result = format(f, ',')
        no_hundreds_place = len(result.split('.')[1]) == 1
        if no_hundreds_place:
            result += '0'
        result += '%'
        return result

    def to_non_fmt_str(self):
        super().__str__()

    def quantize(self, *args, **kwargs):
        return PercentDecimal(super().quantize(*args, **kwargs))

    def __sub__(self, other):
        return PercentDecimal(super().__sub__(other))

    def __add__(self, other):
        return PercentDecimal(super().__add__(other))

    def __mul__(self, other):
        return PercentDecimal(super().__mul__(other))

    def __truediv__(self, other):
        return PercentDecimal(super().__truediv__(other))

    def __floordiv__(self, other):
        return PercentDecimal(super().__floordiv__(other))

    def __mod__(self, other):
        return PercentDecimal(super().__mod__(other))

    def __neg__(self):
        return PercentDecimal(super().__neg__())

    def __pos__(self):
        return PercentDecimal(super().__pos__())

    def __abs__(self):
        return PercentDecimal(super().__abs__())

    def __round__(self, *args, **kwargs):
        return PercentDecimal(super().__round__(*args, **kwargs))

    def __trunc__(self):
        return PercentDecimal(super().__trunc__())

    def __floor__(self):
        return PercentDecimal(super().__floor__())

    def __ceil__(self):
        return PercentDecimal(super().__ceil__())

    def __pow__(self, *args, **kwargs):
        return PercentDecimal(super().__pow__(*args, **kwargs))
