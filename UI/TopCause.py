import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas.tseries.offsets import DateOffset

def settings_cause():
    st.subheader("Paramètres")
    start = st.date_input(
        "Début",
        value=date.today() - relativedelta(years=5),
        min_value=date(2000, 1, 1),
        max_value=date.today(),
        key=4
    )
    end = st.date_input(
        "Fin",
        value=date.today(),
        min_value=date(2000, 1, 1),
        max_value=date.today(),
        key=5
    )
    hide = st.checkbox("Cacher le CD0000")
    return start, end, hide

def display_top_cause(df: pd.DataFrame, hide):
    if hide:
        df = df[df["CAUSE_NAME"] != "CD0000-NATIONAL"]

    st.subheader("🌊Top Cause par Don")
    st.bar_chart(
        data=df,
        x="CAUSE_NAME",
        y="TOTAL_DONS",
    )