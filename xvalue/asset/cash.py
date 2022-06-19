

from typing import TYPE_CHECKING, Any, Type, Union
from numpy import isin
from pydantic import BaseModel

from xvalue.price.forward_curve import ForwardCurve
from .base import Asset

if TYPE_CHECKING:
    from xvalue.asset_class import Currency

class Cash(Asset):
    """A currency position or some amount of currency"""
    amount: float
    asset_class: 'Currency'

    def __init__(self, amount, **kwargs):
        super().__init__(amount=amount, **kwargs)

    def present_value(self, maturity):
        ir_rate = self.interest_rate_curve[maturity]
        return self.amount / ir_rate

    def future_value(self, maturity):
        ir_rate = self.interest_rate_curve[maturity]
        return self.amount * ir_rate

    def convert(self, ccy: 'Currency'):
        "Convert the cash to another currency"
        exchange_rate = self.asset_class[ccy]
        new_amount = self.amount * exchange_rate
        return Cash(amount=new_amount, asset_class=ccy)

    @property
    def interest_rate_curve(self) -> ForwardCurve:
        "Zero cupong interest rate"
        return self.asset_class.interest_rate

    def __eq__(self, other):
        # return comparison
        return self.amount == self._to_comparable_amount(other)

    def _to_comparable_amount(self, other: Union['Cash', float, int]):
        if isinstance(other, (float, int)):
            # Considered as ccy amount of same currency
            return other
        else:
            return other.convert(self.asset_class).amount