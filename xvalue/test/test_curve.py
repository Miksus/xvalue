

import datetime
from xvalue.price.forward_curve import CompoundCurve, ConstantCurve


def test_constant():
    curve = ConstantCurve(rate=2)
    assert curve.rate == 2
    assert 2 == curve['0D'] == curve[0]
    assert curve['700D'] == 2

    curve = ConstantCurve()
    assert curve.rate == 1

def test_compound():
    curve = CompoundCurve(rate=1.02, period="250D")
    assert curve.current == datetime.timedelta()
    assert curve["0D"] == curve[0] == 1.0

    actual = curve.discount(amount=5000, maturity="1000D")
    assert 4619.23 == round(actual, 2)

def test_discounting():

    # Calculated:
    # compounded = 5000 / 1.02^4
    # accural = (5000 / 1.02^5 - 5000 / 1.02^4) * (200 / 250)
    # total = compunded + accrual
    # total = 4546.768665346178
    expected = 4546.768665346178

    # 0.9093537331

    curve = CompoundCurve(rate=1/1.02, period="250D")
    discount_factor = curve["1200D"]
    actual = 5000 * discount_factor
    assert round(expected, 2) == round(actual, 2)

def test_moving():
    # Test moving on the curve to the future

    # Moving full period
    curve = CompoundCurve(rate=1.02, period="250D")
    new_curve = curve.move("250D")

    assert curve.current == datetime.timedelta(0)
    assert new_curve.current == datetime.timedelta(days=250)
    assert new_curve['0D'] == 1.02
    assert new_curve['250D'] == 1.02 ** 2

    # Moving partial period
    new_curve = curve.move("125D")
    assert new_curve['0D'] == 1.01
    assert new_curve['125D'] == 1.02

    # Moving 1 + partial period
    new_curve = new_curve.move("250D")
    assert new_curve.current == datetime.timedelta(days=375)
    assert new_curve['0D'] == 1.0302
    assert new_curve['125D'] == 1.02 ** 2

