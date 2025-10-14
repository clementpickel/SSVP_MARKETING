import streamlit as st
import pandas as pd
from datetime import date
from Model.interval import Interval

def select_settings_bar_chart_ponctuel():
    st.subheader("Paramètres")
    interval = st.selectbox(
        "Intervalle de temps:",
        [Interval.YEAR, Interval.MONTH, Interval.DAY],
        format_func=lambda i: i.value.capitalize(),
        index = 1
    )
    start = st.date_input(
        "Début",
        value=date(2020, 1, 1),
        min_value=date(2000, 1, 1),   # earliest allowed date
        max_value=date.today()         # latest allowed date
    )

    end = st.date_input(
        "Fin",
        value=date.today(),
        min_value=date(2000, 1, 1),
        max_value=date.today()
    )
    agg = False # st.checkbox("Agréger", value=False)
    return interval, start, end, agg

def display_bar_chart_ponctuel(interval: Interval, df: pd.DataFrame):
    if df.empty:
        st.warning("No data available for this interval.")
    else:
        df.columns = [col.capitalize() for col in df.columns]

        # --- Display Chart ---
        if "Total_montantreglement" in df.columns:
            # Find which column is the interval dimension
            interval_col = "Period"
            st.subheader(f"📈 Montant Total par {interval.value.capitalize()}")
            st.bar_chart(
                data=df,
                x=interval_col,
                y="Total_montantreglement",
            )

