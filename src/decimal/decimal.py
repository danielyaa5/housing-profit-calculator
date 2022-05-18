from decimal import Decimal

import src.constants as c


class CustomDecimal(Decimal):
    def to_str_2_digits(self):
        f = self.tenth_place_quantize().__float__()
        str_number = format(f, ',')
        integer_part = str_number.split('.')[0]
        fractional_part = str_number.split('.')[1]
        if fractional_part == '0':
            fractional_part = ''

        if len(fractional_part) == 1:
            fractional_part += '0'

        return f'{integer_part}.{fractional_part}' if fractional_part else integer_part

    def tenth_place_quantize(self):
        return super().quantize(c.TENTH_PLACE_QUANTIZE)
