# -*- encoding: utf-8 -*-
'''
@File    :   coord_T.py
@Time    :   2024/11/22 21:37:06
@Author  :   wenmao Chen 
'''
import streamlit as st
import pandas as pd
from models.coord import gcj02_to_bd09, bd09_to_gcj02, wgs84_to_gcj02, gcj02_to_wgs84, bd09_to_wgs84, wgs84_to_bd09  # 导入坐标转换函数

st.page_link("app.py", label="🏠 首页")
st.sidebar.page_link("app.py", label="🏠 首页")
st.title("坐标转换工具")

# 使用tabs切换单点转换和批量转换
tab1, tab2 = st.tabs(["单点转换", "批量转换"])

with tab1:
    with st.form(key='single_point_form'):
        st.subheader("单点转换")
        col00, col01 = st.columns(2)
        with col00:
            source_system = st.selectbox("源坐标系", ["WGS84", "GCJ-02", "BD-09"])
        with col01:    
            target_system_options = ["WGS84", "GCJ-02", "BD-09"]
            target_system_options.remove(source_system)
            target_system = st.selectbox("目标坐标系", target_system_options)
        
        col1, col2 = st.columns(2)
        with col1:
            lng = st.number_input("经度", value=108.81001)
        with col2:
            lat = st.number_input("纬度", value=36.125376)
        
        submit_button = st.form_submit_button(label='转换')
        
        if submit_button:
            if source_system == "WGS84" and target_system == "GCJ-02":
                result = wgs84_to_gcj02(lng, lat)
            elif source_system == "GCJ-02" and target_system == "WGS84":
                result = gcj02_to_wgs84(lng, lat)
            elif source_system == "GCJ-02" and target_system == "BD-09":
                result = gcj02_to_bd09(lng, lat)
            elif source_system == "BD-09" and target_system == "GCJ-02":
                result = bd09_to_gcj02(lng, lat)
            elif source_system == "BD-09" and target_system == "WGS84":
                result = bd09_to_wgs84(lng, lat)
            elif source_system == "WGS84" and target_system == "BD-09":
                result = wgs84_to_bd09(lng, lat)
            else:
                result = (lng, lat)
            
            st.write(f"转换结果：经度={result[0]}, 纬度={result[1]}")

with tab2:
    st.subheader("批量转换")
    st.info("请上传包含经度和纬度列的CSV文件。\n文件格式示例：")
    st.write(pd.DataFrame({"经度": [120.0, 121.0], "纬度": [30.0, 31.0]}))
    
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        required_columns = {"经度", "纬度"}
        if not required_columns.issubset(df.columns):
            st.error("CSV文件必须包含“经度”和“纬度”两列。")
        else:
            with st.form(key='batch_conversion_form'):
                col1, col2 = st.columns(2)
                with col1:
                    source_system = st.selectbox("源坐标系（批量）", ["WGS84", "GCJ-02", "BD-09"])
                with col2:
                    target_system_options = ["WGS84", "GCJ-02", "BD-09"]
                    target_system_options.remove(source_system)
                    target_system = st.selectbox("目标坐标系（批量）", target_system_options)

                batch_convert_button = st.form_submit_button(label='批量转换')

                if batch_convert_button:
                    results = []
                    for index, row in df.iterrows():
                        lng, lat = row['经度'], row['纬度']
                        if source_system == "WGS84" and target_system == "GCJ-02":
                            result = wgs84_to_gcj02(lng, lat)
                        elif source_system == "GCJ-02" and target_system == "WGS84":
                            result = gcj02_to_wgs84(lng, lat)
                        elif source_system == "GCJ-02" and target_system == "BD-09":
                            result = gcj02_to_bd09(lng, lat)
                        elif source_system == "BD-09" and target_system == "GCJ-02":
                            result = bd09_to_gcj02(lng, lat)
                        elif source_system == "BD-09" and target_system == "WGS84":
                            result = bd09_to_wgs84(lng, lat)
                        elif source_system == "WGS84" and target_system == "BD-09":
                            result = wgs84_to_bd09(lng, lat)
                        else:
                            result = (lng, lat)
                        
                        results.append(result)
                    
                    df['转换后经度'] = [r[0] for r in results]
                    df['转换后纬度'] = [r[1] for r in results]
                    st.dataframe(df)


# 添加一些样式
st.markdown("""
<style>
body {
    font-family: Arial, sans-serif;
}
</style>
""", unsafe_allow_html=True)