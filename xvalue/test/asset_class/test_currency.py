
import pytest

from xvalue.asset_class import Currency
from xvalue.asset import Cash
from xvalue.price.forward_curve import CompoundCurve

@pytest.fixture(autouse=True, scope="function")
def cleanup():
    yield
    Currency.defined_currencies = set()

def test_currency():
    EUR = Currency(code='EUR')
    cash = EUR(500)
    assert isinstance(cash, Cash)
    assert cash.amount == 500
    assert cash.asset_class is EUR

def test_present_value():
    EUR = Currency(code='EUR', interest_rate=CompoundCurve.from_daily(annual_rate=1.01))
    cash = EUR(500)
    assert round(cash.present_value("365D"), 5) == round(500 / 1.01, 5)
    assert round(cash.present_value("730D"), 5) == round(500 / (1.01 ** 2), 5)

def test_future_value():
    EUR = Currency(code='EUR', interest_rate=CompoundCurve.from_daily(annual_rate=1.01))
    cash = EUR(500)
    assert round(cash.future_value("365D"), 5) == round(500 * 1.01, 5)
    assert round(cash.future_value("730D"), 5) == round(500 * (1.01 ** 2), 5)

def test_currency_conversion():

    EUR = Currency(code='EUR')
    USD = Currency(code="USD")

    EUR.exchange_rates = {'USD': 1.1}
    USD.exchange_rates = {'EUR': 1/1.1}

    eur_cash = EUR(500)
    usd_cash = USD(550)
    
    assert eur_cash.convert(USD) == USD(550)
    assert usd_cash.convert(EUR) == EUR(500)

def test_exchange_rates():
    EUR = Currency(code='EUR')
    USD = Currency(code="USD")

    EUR.exchange_rates = {'USD': 1.1}
    USD.exchange_rates = {'EUR': 1/1.1}

    assert EUR[USD] == EUR['USD'] == 1.1
    assert USD[EUR] == USD['EUR'] == 1/1.1

    # Test setitem
    EUR[USD] = 1.11
    assert EUR.exchange_rates['USD'] == 1.11
    EUR['USD'] = 1.111
    assert EUR.exchange_rates['USD'] == 1.111