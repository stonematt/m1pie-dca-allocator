"""Main entry point for the M1 Pie DCA Allocator Streamlit app."""

import streamlit as st
import os
from scripts.log_util import app_logger
from scripts.st_sidepanel import render_sidepanel
from scripts.st_mainpanel import render_mainpanel

logger = app_logger(__name__)

# Set up app-wide environment variables
if "DATA_DIR" not in st.session_state:
    st.session_state["DATA_DIR"] = "data"

os.makedirs(st.session_state["DATA_DIR"], exist_ok=True)

# Configure page
st.set_page_config(page_title="M1 Pie DCA Allocator", layout="wide")

# Render sidebar and main content
render_sidepanel()
render_mainpanel()
