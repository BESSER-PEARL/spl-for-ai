import sys

import streamlit as st
from streamlit.web import cli as stcli

from frontend.create import create
from frontend.sidebar import sidebar_menu

st.set_page_config(layout="wide")

if __name__ == "__main__":
    if st.runtime.exists():
        with st.sidebar:
            page = sidebar_menu()
        if page == 'Home':
            create()

    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
