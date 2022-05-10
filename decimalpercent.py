from decimaldollar import DecimalDollar
import constants as c


class DecimalPercent(DecimalDollar):
    def __format__(self, *args, **kwargs):
        f = super().quantize(c.TENTH_PLACE_QUANTIZE).__float__()
        result = format(f, ',')
        no_hundreds_place = len(result.split('.')[1]) == 1
        if no_hundreds_place:
            result += '0'
        result += '%'
        return result

    def quantize(self, *args, **kwargs):
        return DecimalPercent(super().quantize(*args, **kwargs))

    def __sub__(self, other):
        return DecimalPercent(super().__sub__(other))

    def __add__(self, other):
        return DecimalPercent(super().__add__(other))

    def __mul__(self, other):
        return DecimalPercent(super().__mul__(other))

    def __truediv__(self, other):
        return DecimalPercent(super().__truediv__(other))

    def __floordiv__(self, other):
        return DecimalPercent(super().__floordiv__(other))

    def __mod__(self, other):
        return DecimalPercent(super().__mod__(other))

    def __neg__(self):
        return DecimalPercent(super().__neg__())

    def __pos__(self):
        return DecimalPercent(super().__pos__())

    def __abs__(self):
        return DecimalPercent(super().__abs__())

    def __round__(self, *args, **kwargs):
        return DecimalPercent(super().__round__(*args, **kwargs))

    def __trunc__(self):
        return DecimalPercent(super().__trunc__())

    def __floor__(self):
        return DecimalPercent(super().__floor__())

    def __ceil__(self):
        return DecimalPercent(super().__ceil__())

    def __pow__(self, *args, **kwargs):
        return DecimalPercent(super().__pow__(*args, **kwargs))

    def __radd__(self, other):
        return DecimalPercent(super().__radd__(other))
