import pandas as pd
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

    main_view = st.container()
    result_view = st.container()
    log_view = st.expander("(参考)計算ログ", expanded=False)

    # 線種を選択
    wire_type = st.sidebar.selectbox("線種", [wire.type for wire in wires], index=47)
    wire = next((wire for wire in wires if wire.type == wire_type), None)
    with st.sidebar.expander("線種の詳細", expanded=True):
        st.write(f"線種: {wire.name}")
        st.write(f"計算断面積: {wire.cross_section * 10 ** 6} mm2")
        st.write(f"外径: {wire.diameter * 1000} mm")
        st.write(f"単位重量: {wire.weight} N/m")
        st.write(f"弾性係数: {wire.elastic_modulus / 10 ** 9} e9 N/m2")
        st.write(f"線膨張係数: {wire.thermal_expansion} e-6 /℃")

    # ち度・張力計算の条件を設定
    calc_tension = st.sidebar.toggle("張力を計算する")
    span = st.sidebar.number_input("径間長(m)", value=50.0, step=0.5)
    if calc_tension:
        dip = st.sidebar.number_input("ち度(m)", value=0.05, step=0.05)
        tension = wdt.tension_calc(wire, span, dip)
    else:
        tension = st.sidebar.number_input("張力(kN)", value=9.8, step=4.9) * 1000
        dip = wdt.dip_calc(wire, span, tension)

    is_inclined = st.sidebar.toggle("斜ち度の場合", value=False)
    if is_inclined:
        height1 = st.sidebar.number_input("支持点1の高さ(m)", value=10.0, step=0.5)
        height2 = st.sidebar.number_input("支持点2の高さ(m)", value=10.0, step=0.5)
    else:
        height1 = st.sidebar.number_input("支持点の高さ(m)", value=10.0, step=0.5)
        height2 = None

    # 温度変化がある場合の計算
    calc_temperature = st.sidebar.toggle("温度変化がある場合の計算", value=False)
    if calc_temperature:
        t1 = st.sidebar.number_input("最低温度(℃)", value=-20.0, step=1.0)
        t0 = st.sidebar.number_input("基準温度(℃)", value=10.0, step=1.0)
        t2 = st.sidebar.number_input("最高温度(℃)", value=40.0, step=1.0)
        dip_t1, tension_t1 = wdt.calc_dip_tension_with_temperature(wire, span, tension, t1, t0)
        dip_t2, tension_t2 = wdt.calc_dip_tension_with_temperature(wire, span, tension, t2, t0)
    else:
        t0 = st.sidebar.number_input("基準温度(℃)", value=10.0, step=1.0)

    # グラフデータの作成
    # 標準温度での電線のカテナリを計算する
    x, y, span_a = wdt.catenary_calc(wire, span, tension, dip, height1, height2)
    df_lines = pd.DataFrame({'x': x, 'y': y, '状態': ['標準温度'] * len(x)})
    
    # 結果表示用のデータフレームを作成
    result_data = [{
        '状態': f'基準温度 {t0}℃',
        'ち度 (mm)': f'{dip*1000:.2f}',
        '最大ち度位置 (m)': f'{span_a:.2f}',
        '張力 (kN)': f'{tension/1000:.2f}'
    }]
    
    if calc_temperature:
        x_t1, y_t1, span_a_t1 = wdt.catenary_calc(wire, span, tension_t1, dip_t1, height1, height2)
        x_t2, y_t2, span_a_t2 = wdt.catenary_calc(wire, span, tension_t2, dip_t2, height1, height2)
        df_temp1 = pd.DataFrame({'x': x_t1, 'y': y_t1, '状態': [f'{t1}℃'] * len(x_t1)})
        df_temp2 = pd.DataFrame({'x': x_t2, 'y': y_t2, '状態': [f'{t2}℃'] * len(x_t2)})
        df_lines = pd.concat([df_lines, df_temp1, df_temp2], ignore_index=True)
        
        # 温度変化時のデータを結果テーブルに追加
        result_data.append({
            '状態': f'最低温度 {t1}℃',
            'ち度 (mm)': f'{dip_t1*1000:.2f}',
            '最大ち度位置 (m)': f'{span_a_t1:.2f}',
            '張力 (kN)': f'{tension_t1/1000:.2f}'
        })
        result_data.append({
            '状態': f'最高温度 {t2}℃',
            'ち度 (mm)': f'{dip_t2*1000:.2f}',
            '最大ち度位置 (m)': f'{span_a_t2:.2f}',
            '張力 (kN)': f'{tension_t2/1000:.2f}'
        })
    
    # 結果を表形式で表示
    result_view.dataframe(pd.DataFrame(result_data), hide_index=True)
    

    # plotly で Line Plot を描画
    fig = px.line(df_lines, x='x', y='y', color='状態', 
                  title='電線カテナリ曲線',
                  labels={'x': '水平距離 (m)', 'y': '高さ (m)'})
    
    # グラフの体裁を整える
    fig.update_layout(
        legend_title_text='',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    main_view.plotly_chart(fig)

    log_view.dataframe(df_lines)

    return


    if is_inclined:
        x, y, span_a = wdt.catenary_calc(wire, span, tension, dip, height1, height2)
        if calc_temperature:
            x_t, y_t, span_a_t = wdt.catenary_calc(wire, span, tension_t, dip_t, height1, height2)
        st.write(f"ち度: {dip*1000:.2f}mm (最大ち度位置: {span_a:.2f}m)   張力: {tension/1000:.2f}kN")
    else:
        x, y = wdt.catenary_calc(wire, span, tension, dip, height1)
        if calc_temperature:
            x_t, y_t = wdt.catenary_calc(wire, span, tension_t, dip_t, height1)
        st.write(f"ち度: {dip*1000:.2f}mm (最大ち度位置: {span/2:.2f}m)   張力: {tension/1000:.2f}kN")

    # 電線のカテナリを plotly でグラフ化して表示する
    # 温度変化での計算を行った場合は、1つのグラフビューに、標準温度のグラフと温度変化後のグラフの2つを重ねて表示する
    if calc_temperature:
        fig = px.line(x=x, y=y)
        fig.add_trace(px.line(x=x_t, y=y_t))
        st.plotly_chart(fig)
    else:
        fig = px.line(x=x, y=y)
        st.plotly_chart(fig)



if __name__ == "__main__":
    main()
