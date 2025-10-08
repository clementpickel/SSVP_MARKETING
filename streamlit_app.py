import streamlit as st
from Service.MarketingService import MarketingService, cache_get_reglement_regulier
from UI.BarChartTotalReglementPonctuel import display_bar_chart_ponctuel, select_settings_bar_chart_ponctuel
from Model.interval import Interval
import numpy as np
from datetime import date

st.set_page_config(layout="wide")
st.title("Marketing SSVP")

ms = MarketingService()
# st.text("Work in progress")
# st.dataframe(ms.get_reglement_regulier(Interval.YEAR))

col1, col2 = st.columns([1, 9])
df = cache_get_reglement_regulier(Interval.MONTH, date(2020, 1, 1), date.today(), False)
table = False
with col1:
    interval, start, end, agg, table = select_settings_bar_chart_ponctuel()
with col2:
    df = cache_get_reglement_regulier(interval, start, end, agg)
    display_bar_chart_ponctuel(interval, df, table)

# st.sidebar.header("Settings")
# interval = st.sidebar.selectbox(
#     "Select time interval:",
#     [Interval.YEAR, Interval.MONTH, Interval.DAY],
#     format_func=lambda i: i.value.capitalize()
# )

