# -*- encoding: utf-8 -*-
'''
@File    :   coord_T.py
@Time    :   2024/11/22 21:37:06
@Author  :   wenmao Chen 
'''
import streamlit as st
import pandas as pd
from models.coord import gcj02_to_bd09, bd09_to_gcj02, wgs84_to_gcj02, gcj02_to_wgs84, bd09_to_wgs84, wgs84_to_bd09  # 导入坐标转换函数
pd.set_option('display.float_format', '{:.8f}'.format)

st.sidebar.page_link("app.py", label="🏠 首页")
st.title("坐标转换工具")

# 使用tabs切换单点转换和批量转换
tab1, tab2 = st.tabs(["单点转换", "批量转换"])



with tab1:
    col00, col01 = st.columns(2)
    with col00:
        source_system = st.selectbox("源坐标系", ["WGS84", "GCJ-02", "BD-09"])
    with col01:    
        target_system_options = ["WGS84", "GCJ-02", "BD-09"]
        target_system_options.remove(source_system)
        target_system = st.selectbox("目标坐标系", target_system_options)        
    col1, col2 = st.columns(2)
    # 经度输入
    with col1:
        lng_input = st.text_input("经度", "108.8100188")
        try:
            lng = float(lng_input)
        except ValueError:
            st.error("请输入有效的数字作为经度")

    # 纬度输入
    with col2:
        lat_input = st.text_input("纬度", "36.12537688")
        try:
            lat = float(lat_input)
        except ValueError:
            st.error("请输入有效的数字作为纬度")

    
    # submit_button = st.button(label='转换')
    left, middle, right = st.columns(3)

    if left.button("转换"):
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
        st.write(f"转换结果：经度={result[0]:.8f}, 纬度={result[1]:.8f}")




with tab2:
    # st.subheader("批量转换")
    st.info("请上传包含经度和纬度列的文件")    
    uploaded_file = st.file_uploader("上传文件", type=["xlsx","xls","csv"])
    
    if uploaded_file is not None:
    # 获取文件名和扩展名
        file_name = uploaded_file.name
        file_extension = file_name.split('.')[-1]

        # 根据文件扩展名选择读取方法
        if file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        elif file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        else:
            st.error("不支持的文件类型")

        required_columns = {"经度", "纬度"}
        if not required_columns.issubset(df.columns):
            st.error("CSV文件必须包含“经度”和“纬度”两列。")
        else:
            col1, col2  = st.columns(2)
            with col1:
                source_system = st.selectbox("源坐标系（批量）", ["WGS84", "GCJ-02", "BD-09"])
            with col2:
                target_system_options = ["WGS84", "GCJ-02", "BD-09"]
                target_system_options.remove(source_system)
                target_system = st.selectbox("目标坐标系（批量）", target_system_options)


            batch_convert_button = st.button(label='批量转换')

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
                        result = (format(lng, '.8f'), format(lat, '.8f'))
                    
                    results.append(result)
                
                df['转换后经度'] = [r[0] for r in results]
                df['转换后纬度'] = [r[1] for r in results]
                df