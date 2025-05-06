import numpy as np
from scipy.optimize import fsolve
from src.wire_db import Wire


def dip_calc(wire: Wire, span: float, tension: float) -> float:
    """
    弛度計算(温度変化がない場合)
    Args:
        weight: 単位重量(kg/m)
        span: 径間長(m)
        tension: 張力(N)
    Returns:
        dip: 弛度(m)
    """
    if wire.weight <= 0 or span <= 0 or tension <= 0:
        raise ValueError("weight, span, tension は正の数である必要があります")
    dip = wire.weight * span * span / (8 * tension)
    return dip


def tension_calc(wire: Wire, span: float, dip: float) -> float:
    """
    張力計算(温度変化がない場合)
    Args:
        weight: 単位重量(kg/m)
        span: 径間長(m)
        dip: 弛度(m)
    Returns:
        tension: 張力(N)
    """
    if wire.weight <= 0 or span <= 0 or dip <= 0:
        raise ValueError("weight, span, dip は正の数である必要があります")
    tension = wire.weight * span * span / (8 * dip)
    return tension


def dip_tension_calc(wire: Wire, span: float, dip: float = None, tension: float = None) -> float:
    """
    弛度または張力を計算する。弛度が key args で入力されたら張力を計算し、張力が key args で入力されたら弛度を計算する。
    Args:
        weight: 単位重量(kg/m)
        span: 径間長(m)
        dip: 弛度(m)
        tension: 張力(N)
    Returns:
        dip: 弛度(m)
        tension: 張力(N)
    """
    if wire.weight <= 0 or span <= 0 or dip <= 0 or tension <= 0:
        raise ValueError("weight, span, dip, tension は正の数である必要があります")
    if dip is not None:
        tension = wire.weight * span * span / (8 * dip)
        return tension
    elif tension is not None:
        dip = wire.weight * span * span / (8 * tension)
        return dip
    else:
        raise ValueError("弛度または張力を入力してください")


def calc_dip_tension_with_temperature(wire: Wire, span: float, tension: float, t: float, t0: float) -> float:
    """
    ち度・張力計算(温度変化がある場合)
    Args:
        wire(Wire): 電線のオブジェクト
        span(float): 径間長(m)
        tension(float): 張力(N)
        t(float): 温度(℃)
        t0(float): 基準温度(℃)
    Returns:
        dip(float): 弛度(m)
        tension(float): 張力(N)
    """
    if wire.weight <= 0 or span <= 0 or tension <= 0 or t <= 0 or t0 <= 0:
        raise ValueError("weight, span, tension, t, t0 は正の数である必要があります")
    dip0 = dip_calc(wire, span, tension)
    d_arg2 = 3 * span ** 2 / (8 * wire.cross_section * wire.elastic_modulus) * (tension - wire.cross_section * wire.elastic_modulus * wire.thermal_expansion * (t - t0)) - dip0 ** 2
    d_arg3 = 3 * wire.weight * span ** 4 / (64 * wire.cross_section * wire.elastic_modulus)
    print(f"d_arg2: {d_arg2}, d_arg3: {d_arg3}")
    dip = fsolve(lambda d: d ** 3 + d_arg2 * d + d_arg3, dip0 * 10)    # 初期値は標準温度での弛度の10倍をとりあえず設定
    print(f"dip: {dip}m")
    t_arg2 = tension - 8 * wire.cross_section * wire.elastic_modulus * dip0 ** 2 / (3 * span ** 2) - wire.cross_section * wire.elastic_modulus * wire.thermal_expansion * (t - t0)
    t_arg3 = wire.cross_section * wire.elastic_modulus * wire.weight ** 2 * span ** 2 / 24
    print(f"t_arg2: {t_arg2}, t_arg3: {t_arg3}")
    tension = fsolve(lambda t: t ** 3 - t_arg2 * t - t_arg3, tension)
    print(f"tension: {tension}N")
    return dip[0], tension[0]



def catenary_calc(wire: Wire, span: float, tension: float, dip: float, height1: float, height2: float = None) -> float:
    """
    描画用の電線のカテナリを計算する
    Args:
        wire(Wire): 電線のオブジェクト
        span(float): 径間長(m)
        tension(float): 張力(N)
        dip(float): 弛度(m)
        height1(float): 支持点1の高さ(m)
        height2(float): 支持点2の高さ(m) デフォルトはNone 斜ち度の場合に使用
    Returns:
        x(float): 電線のx座標(m)
        y(float): 電線のy座標(m)
    """
    if wire.weight <= 0 or span <= 0 or tension <= 0 or dip <= 0 or height1 <= 0:
        raise ValueError("weight, span, tension, dip, height1 は正の数である必要があります")
    x = np.linspace(0, span, 100)
    if height2 is None:
        # print("ち度計算")
        y = wire.weight / (2 * tension) * (x - span / 2) ** 2 + (height1 - dip)
        return x, y
    else:
        # print("斜ち度計算")
        span_a = span / 2 - tension * abs(height1 - height2) / (wire.weight * span)
        # print(f"span_a: {span_a}m")
        y = wire.weight / (2 * tension) * (x - span_a) ** 2 + (height1 - dip)
        return x, y, span_a


if __name__ == "__main__":
    weight = 0.6970  # kg/m
    span = 50.0  # m
    tension = 980.0  # N
    dip = dip_calc(weight, span, tension)
    print(f"dip: {dip}m")
    tension = tension_calc(weight, span, dip)
    print(f"tension: {tension}N")

