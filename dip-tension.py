import streamlit as st
import numpy as np
import plotly.express as px

import src.wire_dip_tension as wdt
import src.wire_db as wire_db


def main():
    st.set_page_config(layout="wide")

    # 電線データベースを読み込む
    fpath = "config/wire_db.csv"
    wires = wire_db.Wire.from_csv(fpath)

    st.title("電線 ち度・張力")

    st.sidebar.title("条件を入力")

    # 線種を選択
    wire_type = st.sidebar.selectbox("線種", [wire.type for wire in wires], index=47)
    wire = next((wire for wire in wires if wire.type == wire_type), None)
    weight = wire.weight
    st.sidebar.write(f"線種: {wire.name}")
    st.sidebar.write(f"計算断面積: {wire.cross_section}mm2")
    st.sidebar.write(f"外径: {wire.diameter}mm")
    st.sidebar.write(f"単位重量: {wire.weight}N/m")

    # ち度・張力計算の条件を設定
    calc_tension = st.sidebar.toggle("張力を計算する")
    span = st.sidebar.number_input("径間長(m)", value=50.0, step=0.5)
    if calc_tension:
        dip = st.sidebar.number_input("ち度(m)", value=0.05, step=0.05)
        tension = wdt.tension_calc(weight, span, dip)
    else:
        tension = st.sidebar.number_input("張力(N)", value=980.0, step=98.0)
        dip = wdt.dip_calc(weight, span, tension)

    is_inclined = st.sidebar.toggle("斜ち度の場合", value=False)
    if is_inclined:
        height1 = st.sidebar.number_input("支持点1の高さ(m)", value=10.0, step=0.5)
        height2 = st.sidebar.number_input("支持点2の高さ(m)", value=10.0, step=0.5)
    else:
        height1 = st.sidebar.number_input("支持点の高さ(m)", value=10.0, step=0.5)
        height2 = None

    
    if is_inclined:
        x, y, span_a = wdt.catenary_calc(weight, span, tension, dip, height1, height2)
        st.write(f"ち度: {dip*1000:.2f}mm (最大ち度位置: {span_a:.2f}m)   張力: {tension/1000:.2f}kN")
    else:
        x, y = wdt.catenary_calc(weight, span, tension, dip, height1, height2)
        st.write(f"ち度: {dip*1000:.2f}mm (最大ち度位置: {span/2:.2f}m)   張力: {tension/1000:.2f}kN")

    # 電線のカテナリを plotly でグラフ化して表示する
    fig = px.line(x=x, y=y)
    st.plotly_chart(fig)


if __name__ == "__main__":
    main()
