from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from src.decimal.dollar import Dollar
from src.decimal.percent import Percent

if TYPE_CHECKING:
    pass


class BreakdownRow(ABC, object):
    def dict(self):
        def should_fmt(v):
            return isinstance(v, Dollar) or isinstance(v, Percent)

        def _key(k):
            if k.startswith('monthly_'):
                return k[8:]
            if k.startswith('yearly_'):
                return k[7:]
            return k

        return {
            _key(k): (f'{v}' if should_fmt(v) else v) for (k, v) in self.__dict__.items() if not k.startswith('_')
        }
