from dataclasses import dataclass
import pandas as pd

@dataclass
class Wire:
    type: str  # 呼称
    name: str  # 線種
    cross_section: float  # 計算断面積(mm2)
    diameter: float  # 外径(mm)
    weight: float  # 単位重量(N/m)
    resistance: float  # 電気抵抗(Ω/km at 20℃)
    temp_coef: float  # 抵抗温度係数(/℃)
    breaking_strength: float  # 破壊強度(kN)
    safety_factor: float  # 安全率
    elastic_modulus: float  # 弾性係数(N/m2 ×109)
    thermal_expansion: float  # 線膨張係数×10-6
    
    @classmethod
    def from_csv(cls, csv_path: str) -> list['Wire']:
        """CSVファイルからWireオブジェクトのリストを生成する"""
        df = pd.read_csv(csv_path, encoding='utf-8')
        wires = []
        
        for _, row in df.iterrows():
            wire = cls(
                type=row['呼称'],
                name=row['線種'],
                cross_section=row['計算断面積(mm2)'] / 10 ** 6,
                diameter=row['外径(mm)'] / 1000,
                weight=row['単位重量(N/m)'],
                resistance=row['電気抵抗(Ω/km at 20℃)'],
                temp_coef=row['抵抗温度係数(/℃)'],
                breaking_strength=row['破壊強度(kN)'],
                safety_factor=row['安全率'],
                elastic_modulus=row['弾性係数(N/m2 ×109)']*10**9,
                thermal_expansion=row['線膨張係数×10-6']*10**-6
            )
            wires.append(wire)
        
        return wires
    
