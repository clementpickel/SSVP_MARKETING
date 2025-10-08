import streamlit as st
from Service.MarketingService import MarketingService
import numpy as np

st.set_page_config(layout="wide")
with st.container():
    _, main, _ = st.columns([1,2,1])
    with main:
        st.title("Marketing SSVP")

ms = MarketingService()
st.text("Work in progress")