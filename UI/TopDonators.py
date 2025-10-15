import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas.tseries.offsets import DateOffset

def settings_top_donator():
    st.subheader("Paramètres")
    start = st.date_input(
        "Début",
        value=date.today() - relativedelta(years=1),
        min_value=date(2000, 1, 1),
        max_value=date.today(),
        key=0
    )
    end = st.date_input(
        "Fin",
        value=date.today(),
        min_value=date(2000, 1, 1),
        max_value=date.today(),
        key=1
    )
    limit = st.number_input("Limite", value=10, min_value=1, step=1)
    return start, end, limit

def display_top_donators(df):
    st.subheader("💰 Top donateurs")
    st.dataframe(df)




