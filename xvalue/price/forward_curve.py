

import copy
import matplotlib.pyplot as plt
import datetime
from typing import List, Literal, Optional, Union
import numpy as np
from pydantic import BaseModel, Field, validator
import pandas as pd

class ForwardPoint(BaseModel):
    value: float
    maturity: datetime.timedelta


class ForwardCurve(BaseModel):
    """Forward curve

    Forward curve defines the price at which an asset
    can be delivered at a future date.

    Forward curve is not necessarily the same as market 
    prediction of the spot price due to contango: forward
    price has the interest and cost of storage embedded into
    it.

    Parameters
    ----------
    BaseModel : _type_
        _description_
    """
    current: datetime.timedelta = Field(description="Where we are currently on the curve. By default at the beginning.", default=datetime.timedelta())

    def __getitem__(self, maturity):
        "Get curve value at given datetime(s)"
        array_like = (list, tuple, np.ndarray, pd.Index, pd.Series)
        if isinstance(maturity, array_like):
            maturities = maturity
            if isinstance(maturity, pd.TimedeltaIndex):
                # to prevent the results being fractions of days instead of floats
                type_ = pd.Index
            else:
                type_ = type(maturities)
            return type_(self[maturity] for maturity in maturities)
        else:
            maturity = self.current + self.to_timedelta(maturity)
            return self.at(maturity)

    def at(self, maturity):
        "Get curve value at given maturity"
        raise NotImplementedError()
        
    def move(self, maturity:str) -> 'ForwardCurve':
        "Move to the future on the curve"
        attrs = vars(self).copy()
        attrs['current'] = attrs['current'] + self.to_timedelta(maturity)
        model = type(self)
        return model(**attrs)
        

    def discount(self, amount: float, maturity):
        "Turn future value to present value"
        curve_value = self.at(maturity)
        return amount / curve_value

    def compound(self, amount, maturity):
        "Turn present value to future value"
        curve_value = self.at(maturity)
        return amount * curve_value

    def plot_fixed(self, start: datetime.date=None, end:Union[datetime.date, datetime.timedelta]=None, step:datetime.timedelta=None):
        start = datetime.date.today() if start is None else start
        end = start + pd.offsets.DateOffset(years=10) if end is None else start + end if isinstance(end, datetime.timedelta) else end
        step = datetime.timedelta(days=1) if step is None else step
        x = pd.date_range(start, end, freq=step)
        y = self[x - pd.Timestamp(start)]
        plt.plot(x, y)

    def plot(self, end:datetime.timedelta=None, step:datetime.timedelta=None):
        end = pd.Timedelta(days=365*10) if end is None else end
        step = datetime.timedelta(days=1) if step is None else step

        step = pd.Timedelta(step)
        x = []
        y = []
        for i in range(int(end / step)):
            maturity = i * step
            x.append(maturity.days)
            y.append(self[maturity])
        plt.plot(x, y)

    def to_timedelta(self, maturity:str):
        return pd.Timedelta(maturity)


class ConstantCurve(ForwardCurve):

    rate: float = Field(default=1)

    def at(self, maturity):
        "Get curve value at given maturity"
        return self.rate

class CompoundCurve(ForwardCurve):
    """Forward curve that increases with a compound rate

    Useful as a discount rate curve.

    Parameters
    ----------
    ForwardCurve : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    interpolation: Literal['linear', 'step'] = Field(default="linear", description="Interpolation method between compound points.")
    period: datetime.timedelta = Field(description="Compound period.", default=datetime.timedelta(days=365))
    rate: float

    @classmethod
    def from_daily(cls, annual_rate=None, **kwargs):
        "Generate daily compounding from effective rate of different period"
        rate = annual_rate ** (1 / 365)
        return cls(rate=rate, period=datetime.timedelta(days=1), **kwargs)

    @validator("period", pre=True)
    def parse_period(cls, value):
        return pd.Timedelta(value)

    def at(self, maturity):
        "Get curve value at given maturity"
        forward_time = self.to_timedelta(maturity)
        full_periods = self.get_full_periods(forward_time)
        partial_period = self.get_parial_period(forward_time)

        compound_rate = self.rate ** full_periods
        accrual_rate = self.get_accrued(full_periods=full_periods, partial_period=partial_period)
        return compound_rate + accrual_rate

    def get_full_periods(self, mat:datetime.timedelta) -> int:
        "Get number of full compounded periods in the maturity"
        return mat // self.period

    def get_parial_period(self, mat: datetime.timedelta) -> float:
        """Get remaining incomplete period in the maturity
        
        Is between 0 and 1"""
        remainder = mat % self.period
        return remainder / self.period

    def get_accrued(self, partial_period:float, full_periods:int = 0):
        if self.interpolation == "linear":
            # Linear accrual
            # x*r^n + (x*r^(n+1) - x*r^n) * p
            r = self.rate
            n = full_periods
            p = partial_period
            #! TODO: if discount, r should be 1/r
            return p * r ** (n + 1) - p * r ** n
        elif self.interpolation == "step":
            return 0
        else:
            raise KeyError("Invalid interpolation")



default_curve = ConstantCurve(value=1.0)