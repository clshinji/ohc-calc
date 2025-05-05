import numpy as np


def dip_calc(weight: float, span: float, tention: float) -> float:
    """
    弛度計算(温度変化がない場合)
    Args:
        weight: 単位重量(kg/m)
        span: 径間長(m)
        tention: 張力(N)
    Returns:
        dip: 弛度(m)
    """
    dip = weight * span * span / (8 * tention)
    return dip


def tention_calc(weight: float, span: float, dip: float) -> float:
    """
    張力計算(温度変化がない場合)
    Args:
        weight: 単位重量(kg/m)
        span: 径間長(m)
        dip: 弛度(m)
    Returns:
        tension: 張力(N)
    """
    tention = weight * span * span / (8 * dip)
    return tention


def catenary_calc(weight: float, span: float, tention: float, dip: float, height1: float, height2: float = None) -> float:
    """
    描画用の電線のカテナリを計算する
    Args:
        weight(float): 単位重量(kg/m)
        span(float): 径間長(m)
        tention(float): 張力(N)
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
        y = weight / (2 * tention) * (x - span / 2) ** 2 + (height1 - dip)
    else:
        # print("斜ち度計算")
        span_a = span / 2 - tention * abs(height1 - height2) / (weight * span)
        # print(f"span_a: {span_a}m")
        y = weight / (2 * tention) * (x - span_a) ** 2 + (height1 - dip)
    return x, y


if __name__ == "__main__":
    weight = 0.6970  # kg/m
    span = 50.0  # m
    tention = 980.0  # N
    dip = dip_calc(weight, span, tention)
    print(f"dip: {dip}m")
    tention = tention_calc(weight, span, dip)
    print(f"tention: {tention}N")

