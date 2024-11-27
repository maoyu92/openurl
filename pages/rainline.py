# -*- encoding: utf-8 -*-
'''
@File    :   rainline.py
@Time    :   2024/11/22 21:50:46
@Author  :   wenmao Chen 
'''

import streamlit as st
import pandas as pd
import math
import datetime
import numpy as np
import plotly.express as px
import os


st.sidebar.page_link("app.py", label="🏠 首页")
def intensity(A, B, C, N, t, P):
    """
    雨强计算。
    参数:
    - a,b,c,n: 参数。
    - p (float): 设计重现期（单位：年）。
    - t (np.ndarray): 分钟数组
    返回:
    - its: 雨强（单位：mm/min）。
    """
    a = A * 0.4 * (1 + C * math.log10(P))
    its = a * ((1 - N) * t + B) / np.power(t + B, N + 1)
    return its

def rainCalc_single_period(A, B, C, N, T: int, p: float, peak_ratio: float):
    """
    计算单一时段内的降雨强度分布。
    参数:
    - T (int): 降雨持续时间（单位：分钟）。
    - p (float): 设计重现期（单位：年）。
    - peak_ratio (float): 雨强峰值所在时间占总降雨历时的比例。

    返回:
    - np.ndarray: 随时间变化的降雨强度数组（单位：mm/min）。
    内部参数:
    - t (np.ndarray): 分钟数组
    - peak_time (float): 峰值时间
    """
    t = np.arange(0, T)
    peak_time = T * peak_ratio
    itAr = np.zeros(len(t))

    # 计算雨强
    for i in range(len(t)):
        if t[i] < peak_time:
            itAr[i] = intensity(A, B, C, N, (peak_time - t[i]) / peak_ratio, p) / 60
        else:
            itAr[i] = intensity(A, B, C, N, (t[i] - peak_time) / peak_ratio, p) / 60
    return itAr

# 新增判断逻辑
def check_duplicate(province, county, data):
    """检查省份和区县组合是否已存在"""
    existing_records = data[(data["省份"] == province) & (data["区县"] == county)]
    if not existing_records.empty:
        return True  # 数据已存在
    return False

# 加载Excel数据
@st.cache_data
def load_data():
    file_path = "pages/datas/raincode.xlsx"
    if not os.path.exists(file_path):
        st.error(f"文件 {file_path} 不存在，请确保文件位于与脚本相同的目录下。")
        return None
    return pd.read_excel(file_path)

data = load_data()

if data is None:
    st.stop()  # 如果数据加载失败，停止应用

# 页面布局
st.title("暴雨径流量及雨型生成器")

# 侧边栏菜单
page = st.sidebar.selectbox("选择模式", ["预定义暴雨强度公式", "自定义暴雨强度公式"])

# 预定义暴雨强度公式页面
if page == "预定义暴雨强度公式":
    st.markdown("### 预定义暴雨强度公式")
    # 下拉选择城市
    province = st.sidebar.selectbox(
        "选择省份", data["省份"].unique(), index=data["省份"].unique().tolist().index("重庆市")
    )

    # 根据所选省份筛选区县
    city_options = data[data["省份"] == province]["区县"].unique()
    try:
        default_city_index = city_options.tolist().index("永川区")
    except ValueError:
        default_city_index = 0  # 如果永川不存在于列表中，选择第一个区县作为默认
    city = st.sidebar.selectbox("选择区县", city_options, index=default_city_index)

    # 之后可以根据选定的省份和区县进行进一步的数据处理
    selected_row = data[(data["省份"] == province) & (data["区县"] == city)]
    if not selected_row.empty:
        A, B, C, N = selected_row[["A", "B", "C", "N"]].values[0]
        # 显示选中城市的暴雨公式参数
        st.write(f"**{province}{city} 的暴雨公式参数**")
        st.markdown(
            r"""
        $$
        q=\frac{A(1+C\cdot\log(P))}{(t+B)^N}
        $$
        """
        )
        st.write(f"A={A}, B={B}, C={C}, N={N}")
        # 降雨强度参数输入
        P = st.sidebar.number_input("重现期P(年)", min_value=1, value=10)
        duration_minutes = st.sidebar.number_input(
            "暴雨历时（分钟）", min_value=1, max_value=1440, value=60
        )
        peak_ratio = st.sidebar.slider(
            "峰值比例", min_value=0.0, max_value=1.0, step=0.01, value=0.35
        )
        start_date = st.sidebar.date_input("选择日期", datetime.date.today())
        # 生成雨型按钮
        if st.sidebar.button("生成雨型"):
            # 检查P和t是否已输入
            if P and duration_minutes:
                # 计算暴雨强度q
                q = (A * (1 + C * math.log10(P))) / ((duration_minutes + B) ** N)
                timestamps = pd.date_range(
                    start=start_date, periods=duration_minutes + 1, freq="T"
                )[
                    :-1
                ]  # 减去最后一个是因为range包含结束时间
                # st.write("暴雨时间序列起始时间为:", timestamps[0], "至", timestamps[-1])

                itAr_value = rainCalc_single_period(
                    A, B, C, N, duration_minutes, P, peak_ratio
                )
                df = pd.DataFrame(
                    {"Time": timestamps, "Rain Intensity (mm/min)": itAr_value}
                )
                Q_all = df["Rain Intensity (mm/min)"].sum()

                st.write(
                    f"重现期{P}年,降雨历时{duration_minutes}分钟, 累计雨量{Q_all:.2f}mm,暴雨强度{q:.2f} L/s·hm2"
                )
                # 使用Plotly绘制交互式折线图
                fig = px.line(
                    df,
                    x="Time",
                    y="Rain Intensity (mm/min)",
                    title="芝加哥暴雨曲线",
                    color_discrete_sequence=["red"],  # 设置折线颜色为红色
                )

                # 修改横坐标时间格式
                fig.update_layout(
                    xaxis_title="时间",
                    xaxis_tickformat="%Y-%m-%d %H:%M:%S",  # 设置时间格式
                )

                # 使用tabs切换单点转换和批量转换
                tab1, tab2 = st.tabs(["雨型曲线", "雨型数据"])
                with tab1:
                    st.plotly_chart(fig)
                with tab2:
                    st.dataframe(df)

            else:
                st.warning("请确保已输入重现期P(年)和暴雨历时（分钟）。")

        # 雨水流量参数输入
        s_hectares = st.sidebar.number_input("汇水面积s（公顷）", min_value=1.0, value=2000.0)
        phi = st.sidebar.slider(
            "径流系数φ", min_value=0.0, max_value=1.0, step=0.01, value=0.45
        )

        if st.sidebar.button("计算雨水流量"):
            # 实际雨水流量计算逻辑
            # 确保暴雨强度q已计算

            if "q" not in locals():
                if P and duration_minutes:
                    # 重新计算q，确保在需要时可用
                    q = (A * (1 + C * math.log10(P))) / (duration_minutes + B) ** N
                else:
                    st.warning("请先计算暴雨强度q，确保已输入重现期P(年)和暴雨历时（分钟）。")
                    q = None

            if q is not None:  # 如果q已成功计算
                # 计算雨水流量Q（L/s）
                Q_l_per_s = (
                    q * phi * s_hectares
                )
                # 转换雨水流量为立方米每天（m³/d）
                hours_in_day = 24
                minutes_in_hour = 60
                seconds_in_minute = 60
                Q_m3_per_d = (
                    Q_l_per_s
                    * (hours_in_day * minutes_in_hour * seconds_in_minute)
                    / 1000
                )  # 从L/s转换为m³/d，1m³=1000L
                # 输出结果
                st.markdown("##### 雨水流量计算结果")

                st.write(
                    f" 重现期{P}年,降雨历时{duration_minutes}分钟, 暴雨强度{q:.2f} L/s·hm2,流域面积{s_hectares}公顷，径流系数为{phi}，流量为 {Q_l_per_s:.2f} L/s,累计汇水量{Q_m3_per_d:.2f} m³"
                )
            else:
                st.warning("无法计算雨水流量，因为暴雨强度q未计算。请先确保所有必需参数已输入并计算q。")

# 自定义暴雨强度公式页面
elif page == "自定义暴雨强度公式":
    st.markdown("### 自定义暴雨强度公式")

    # 输入省份和区县
    province = st.sidebar.text_input("省份")
    county = st.sidebar.text_input("区县")

    # 自定义常数项输入

    A = st.sidebar.number_input("A")
    B = st.sidebar.number_input("B", step=0.001)
    C = st.sidebar.number_input("C", step=0.001)
    N = st.sidebar.number_input("N", step=0.001)

    # 公式预览按钮
    if st.sidebar.button("公式预览"):
        st.write(f"省份：{province}\n区县：{county}\n公式参数：A={A}, B={B}, C={C}, N={N}")
        # 用户选择了省份和区县之后
        if province and county:
            duplicate = check_duplicate(province, county, data)

            if duplicate:
                st.warning("数据已存在，请勿重复添加。")
            else:
                # 这里可以添加处理新数据的逻辑，比如保存到数据库或进一步的数据处理
                st.success("数据有效，可以继续下一步操作...")
        else:
            st.info("请先选择省份和区县。")

    # 确认添加按钮
    if st.sidebar.button("确认添加"):
        if (
            not province
            or not county
            or A is None
            or B is None
            or C is None
            or N is None
            or (A == 0 and B == 0 and C == 0 and N == 0)
        ):
            st.error("请先完善相关参数信息，确保省份、区县以及A、B、C、N均不为空或为0。")
        else:
            # 新增行数据
            new_entry = pd.DataFrame(
                {
                    "序号": [data["序号"].max() + 1],
                    "省份": [province],
                    "区县": [county],
                    "A": [A],
                    "B": [B],
                    "C": [C],
                    "N": [N],
                }
            )

            # 将新数据追加到DataFrame
            data = pd.concat([data, new_entry])
            data = data.reset_index(drop=True)

            # 保存回Excel文件
            data.to_excel("raincode.xlsx", index=False)
            st.success("公式已成功添加至数据库！")
            st.markdown("### 新参数表")
            st.dataframe(data)

            # 清除输入框，以便下一次输入
            province = ""
            county = ""

            A = B = C = N = None






