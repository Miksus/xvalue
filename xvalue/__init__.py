from xvalue import asset_class
from . import asset, asset_class

asset.Cash.update_forward_refs(Currency=asset_class.Currency)