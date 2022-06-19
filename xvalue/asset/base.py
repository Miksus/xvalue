

from abc import abstractmethod
from pydantic import BaseModel

class Asset(BaseModel):

    @abstractmethod
    def present_value(self, maturity):
        """Turn the value of the asset on future date to current date
        
        For example, cash must take into account interest rate, commodities
        the storaging costs"""