

from typing import ClassVar, Dict, List, Set, Type, Union
from pydantic import BaseModel, Field, ValidationError, validator
from xvalue.asset import Cash, Asset

from xvalue.price import ForwardCurve, CompoundCurve, default_curve
from .base import AssetClass

class Currency(AssetClass):
    """Currency 

    This class represents a specific currency, ie. EUR, USD or SEK.
    This class is not a currency position and there is ``Cash`` for that
    purpose.
    """
    code: str
    interest_rate: ForwardCurve = Field(default=default_curve)
    exchange_rates: Dict[str, float] = Field(description="Exchange rates to convert the currency to another currency", default={})

    asset_cls = Cash

    defined_currencies: ClassVar[Set[str]] = set()

    def __getitem__(self, ccy: Union['Currency', str]) -> float:
        "Get conversion/exchange rate"
        ccy_code = ccy.code if isinstance(ccy, Currency) else ccy
        is_same = self.code == ccy_code
        if is_same:
            return 1.0
        return self.exchange_rates[ccy_code]

    def __setitem__(self, ccy: Union['Currency', str], value:float):
        "Set conversion/exchange rate"
        ccy_code = ccy.code if isinstance(ccy, Currency) else ccy
        if not isinstance(value, float):
            raise TypeError("Can only set float as exchange rate")
        self.exchange_rates[ccy_code] = value

    @validator('code', pre=True)
    def validate_code(cls, value):
        if value in cls.defined_currencies:
            raise ValidationError("Currency code already exists")
        return value

    @validator('code', pre=False)
    def set_code(cls, value):
        cls.defined_currencies.add(value)
        return value

    @validator('interest_rate', pre=True)
    def parse_interest_rate(cls, value):
        if isinstance(value, float):
            # Considered as yearly interest rate but compunded daily
            value = value ** (1 / 365)
            return CompoundCurve(rate=value, period="1D")
        return value
