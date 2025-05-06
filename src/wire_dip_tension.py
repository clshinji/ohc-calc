import numpy as np
from scipy.optimize import fsolve


def dip_calc(weight: float, span: float, tension: float) -> float:
    """
    弛度計算(温度変化がない場合)
    Args:
        weight: 単位重量(kg/m)
        span: 径間長(m)
        tension: 張力(N)
    Returns:
        dip: 弛度(m)
    """
    dip = weight * span * span / (8 * tension)
    return dip


def tension_calc(weight: float, span: float, dip: float) -> float:
    """
    張力計算(温度変化がない場合)
    Args:
        weight: 単位重量(kg/m)
        span: 径間長(m)
        dip: 弛度(m)
    Returns:
        tension: 張力(N)
    """
    tension = weight * span * span / (8 * dip)
    return tension


def dip_tension_calc(weight: float, span: float, dip: float = None, tension: float = None) -> float:
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
    if dip is not None:
        tension = weight * span * span / (8 * dip)
        return tension
    elif tension is not None:
        dip = weight * span * span / (8 * tension)
        return dip
    else:
        raise ValueError("弛度または張力を入力してください")


def dip_calc_with_temperature(weight: float, span: float, tension: float, t: float, t0: float) -> float:
    """
    弛度計算(温度変化がある場合)
    """
    dip = weight * span * span / (8 * tension)
    return dip



def catenary_calc(weight: float, span: float, tension: float, dip: float, height1: float, height2: float = None) -> float:
    """
    描画用の電線のカテナリを計算する
    Args:
        weight(float): 単位重量(kg/m)
        span(float): 径間長(m)
        tension(float): 張力(N)
        dip(float): 弛度(m)
        height1(float): 支持点1の高さ(m)
        height2(float): 支持点2の高さ(m) デフォルトはNone 斜ち度の場合に使用
    Returns:
        x(float): 電線のx座標(m)
        y(float): 電線のy座標(m)
    """
    x = np.linspace(0, span, 100)
    if height2 is None:
        # print("ち度計算")
        y = weight / (2 * tension) * (x - span / 2) ** 2 + (height1 - dip)
        return x, y
    else:
        # print("斜ち度計算")
        span_a = span / 2 - tension * abs(height1 - height2) / (weight * span)
        # print(f"span_a: {span_a}m")
        y = weight / (2 * tension) * (x - span_a) ** 2 + (height1 - dip)
        return x, y, span_a


if __name__ == "__main__":
    weight = 0.6970  # kg/m
    span = 50.0  # m
    tension = 980.0  # N
    dip = dip_calc(weight, span, tension)
    print(f"dip: {dip}m")
    tension = tension_calc(weight, span, dip)
    print(f"tension: {tension}N")

