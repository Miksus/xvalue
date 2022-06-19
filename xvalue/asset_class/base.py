
from typing import ClassVar, Type
from pydantic import BaseModel

from xvalue.asset import Asset

class AssetClass(BaseModel, copy_on_model_validation=False):
    asset_cls: ClassVar[Type[Asset]]

    def __call__(self, *args, **kwargs):
        "Create an asset instance"
        return self.asset_cls(*args, **kwargs, asset_class=self)