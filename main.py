import sys

import streamlit as st
from streamlit.web import cli as stcli

from frontend.create import create

st.set_page_config(layout="wide")

if __name__ == "__main__":
    if st.runtime.exists():
        create()

    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
