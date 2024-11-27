# -*- encoding: utf-8 -*-
'''
@File    :   app.py
@Time    :   2024/11/22 21:37:26
@Author  :   wenmao Chen 
'''

import streamlit as st
import warnings

st.set_page_config(
    page_title="工具箱",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help': 'https://maoyu92.github.io/',
        'Report a bug': "https://maoyu92.github.io/",
        'About': "# 关于 \n\n"
                 "工具箱\n\n"
                 "@陈文茂"
    }
)


def app():
    # st.write("## 百宝箱")
    st.subheader("工具箱")
    link1, link2, link3, link4 = st.columns(4)

    with link1:
        st.page_link("pages/coord_T.py", label="坐标转换", icon="🏠")
    with link2:
        st.page_link("pages/rainline.py", label="芝加哥雨型", icon="🌧️")






if __name__ == "__main__":
    app()

