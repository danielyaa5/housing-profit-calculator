from src.decimal.decimal import CustomDecimal


class Dollar(CustomDecimal):
    def __format__(self, *args, **kwargs):
        return f'${self.to_str_2_digits()}'

    def quantize(self, *args, **kwargs):
        return Dollar(super().quantize(*args, **kwargs))

    def __sub__(self, other):
        return Dollar(super().__sub__(other))

    def __add__(self, other):
        return Dollar(super().__add__(other))

    def __mul__(self, other):
        return Dollar(super().__mul__(other))

    def __truediv__(self, other):
        return Dollar(super().__truediv__(other))

    def __floordiv__(self, other):
        return Dollar(super().__floordiv__(other))

    def __mod__(self, other):
        return Dollar(super().__mod__(other))

    def __neg__(self):
        return Dollar(super().__neg__())

    def __pos__(self):
        return Dollar(super().__pos__())

    def __abs__(self):
        return Dollar(super().__abs__())

    def __round__(self, *args, **kwargs):
        return Dollar(super().__round__(*args, **kwargs))

    def __trunc__(self):
        return Dollar(super().__trunc__())

    def __floor__(self):
        return Dollar(super().__floor__())

    def __ceil__(self):
        return Dollar(super().__ceil__())

    def __pow__(self, *args, **kwargs):
        return Dollar(super().__pow__(*args, **kwargs))

    def __radd__(self, other):
        return Dollar(super().__radd__(other))

    def __lt__(self, other):
        return Dollar(super().__lt__(other))

    def __le__(self, other):
        return Dollar(super().__le__(other))

    def __eq__(self, other):
        return Dollar(super().__eq__(other))

    def __ne__(self, other):
        return Dollar(super().__ne__(other))

    def __gt__(self, other):
        return Dollar(super().__gt__(other))

    def __ge__(self, other):
        return Dollar(super().__ge__(other))
