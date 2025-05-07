import pytest
import src.wire_dip_tension as wdt


def test_dip_calc():
    # 温度変化がない場合の弛度
    weight = 1.0  # kg/m
    span = 50.0  # m
    tension = 1000.0  # N
    dip = wdt.dip_calc(weight, span, tension)
    assert dip == 0.3125

def test_tension_calc():
    # 温度変化がない場合の張力
    weight = 1.0  # kg/m
    span = 50.0  # m
    dip = 0.5  # m
    tension = wdt.tension_calc(weight, span, dip)
    assert tension == 625.0

def test_negative_values():
    with pytest.raises(ValueError):
        wdt.dip_calc(-1.0, 50.0, 1000.0)
    with pytest.raises(ValueError):
        wdt.tension_calc(-1.0, 50.0, 0.5)

def test_zero_values():
    with pytest.raises(ValueError):
        wdt.dip_calc(0.0, 50.0, 1000.0)
    with pytest.raises(ValueError):
        wdt.tension_calc(1.0, 0.0, 0.5)
    with pytest.raises(ValueError):
        wdt.dip_calc(1.0, 50.0, 0.0)

def test_large_values():
    with pytest.raises(ValueError):
        wdt.dip_calc(1.0, 1000000.0, 1000.0)
    with pytest.raises(ValueError):
        wdt.tension_calc(1.0, 50.0, 1000000.0)

def test_temperature_effect():
    weight = 1.0  # kg/m
    span = 50.0  # m
    tension = 1000.0  # N
    t = 100.0  # 現在の温度
    t0 = 20.0  # 基準温度
    dip = wdt.dip_calc_with_temperature(weight, span, tension, t, t0)
    # 温度が上がると弛度が大きくなるはず
    assert dip > 0.3125  # 基準温度での弛度より大きい

