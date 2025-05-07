import time
from typing import Tuple
import numpy as np
from scipy.optimize import fsolve
from scipy.optimize import newton
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
    dip = wire.weight * span ** 2 / (8 * tension)
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
    tension = wire.weight * span ** 2 / (8 * dip)
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
        tension = wire.weight * span ** 2 / (8 * dip)
        return tension
    elif tension is not None:
        dip = wire.weight * span ** 2 / (8 * tension)
        return dip
    else:
        raise ValueError("弛度または張力を入力してください")


def calc_dip_tension_with_temperature(wire: Wire, span: float, tension: float, t: float, t0: float) -> Tuple[float, float]:
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
    # 必須パラメータのチェック
    if wire.weight <= 0 or span <= 0 or tension <= 0:
        raise ValueError("weight, span, tension は正の数である必要があります")
    
    # 標準温度での弛度の計算
    dip0 = dip_calc(wire, span, tension)

    # 弛度の計算
    # print(">>> 弛度の計算 ------------------------------")
    d_arg2 = 3 * span ** 2 / (8 * wire.cross_section * wire.elastic_modulus) * (tension - wire.cross_section * wire.elastic_modulus * wire.thermal_expansion * (t - t0)) - dip0 ** 2
    d_arg3 = 3 * wire.weight * span ** 4 / (64 * wire.cross_section * wire.elastic_modulus)
    # 弛度の係数 [d^3, d^2, d, 1]
    roots_d = np.roots([1.0, 0.0, d_arg2, -d_arg3])
    # print(f"roots_d: {roots_d}")
    dip_t = float(next(r for r in roots_d if np.isreal(r) and r > 0).real)

    # 張力の計算
    # print(">>> 張力の計算 ------------------------------")
    t_arg2 = tension - 8 * wire.cross_section * wire.elastic_modulus * dip0 ** 2 / (3 * span ** 2) - wire.cross_section * wire.elastic_modulus * wire.thermal_expansion * (t - t0)
    t_arg3 = wire.cross_section * wire.elastic_modulus * wire.weight ** 2 * span ** 2 / 24
    # 張力の係数 [t^3, t^2, t, 1]
    roots_t = np.roots([1.0, -t_arg2, 0.0, -t_arg3])
    # print(f"roots_t: {roots_t}")
    tension_t = float(next(r for r in roots_t if np.isreal(r) and r > 0).real)
    # print(f"tension: {tension_t} N")

    # 弛度の計算結果から簡易式で計算しても結果は同等
    # ⇧の計算に時間がかかるようなら、こっちの方がシンプルで良いかも
    # print(f"簡易式で計算したtension: {wire.weight * span * span / (8 * dip_t)} N")

    return dip_t, tension_t



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
    if wire.weight <= 0 or span <= 0 or tension <= 0 or dip <= 0:
        raise ValueError("weight, span, tension, dip は正の数である必要があります")
    x = np.linspace(0, span, 100)
    if height2 is None:
        # print("ち度計算")
        y = wire.weight / (2 * tension) * (x - span / 2) ** 2 + (height1 - dip)
        return x, y, span / 2
    else:
        # print("斜ち度計算")
        span_a = span / 2 - tension * (height2 - height1) / (wire.weight * span)
        # print(f"span_a: {span_a}m")
        # 元の式: y = wire.weight / (2 * tension) * (x - span_a) ** 2 + (height1 - dip)
        # x=0 で y=height1, x=span で y=height2 となるようにオフセットを計算します。
        # これにより、この分岐では引数 dip は使用されません。
        y_offset = height1 - (wire.weight / (2 * tension)) * span_a ** 2
        y = wire.weight / (2 * tension) * (x - span_a) ** 2 + y_offset
        return x, y, span_a


if __name__ == "__main__":
    weight = 6.83  # N/m
    span = 50.0  # m
    tension = 9800.0  # N
    dip = dip_calc(weight, span, tension)
    print(f"dip: {dip}m")
    tension = tension_calc(weight, span, dip)
    print(f"tension: {tension}N")

