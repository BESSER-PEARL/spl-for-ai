import streamlit as st
import streamlit_antd_components as sac


def sidebar_menu():
    st.header('SPL for AI')
    page = sac.menu([
        sac.MenuItem('Home', icon='house'),
    ], open_all=True)
    return page
