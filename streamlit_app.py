import streamlit as st
from Service.MarketingService import MarketingService, cache_get_reglement_regulier, cache_get_top_donateurs, cache_get_top_donateurs_regulier, cache_get_top_cause
from UI.BarChartTotalReglementPonctuel import display_bar_chart_ponctuel, select_settings_bar_chart_ponctuel
from UI.TopDonators import display_top_donators, settings_top_donator
from UI.ReglementRegulier import display_reglement_regulier, settings_reglement_regulier
from UI.TopCause import settings_cause, display_top_cause
from Model.interval import Interval
import numpy as np
from datetime import date

st.set_page_config(layout="wide")
st.title("Marketing SSVP")

col1, col2 = st.columns([1, 9])
df = cache_get_reglement_regulier(Interval.MONTH, date(2020, 1, 1), date.today(), False)
with col1:
    interval, start, end, agg = select_settings_bar_chart_ponctuel()
with col2:
    df = cache_get_reglement_regulier(interval, start, end, agg)
    display_bar_chart_ponctuel(interval, df)
    
col1, col2 = st.columns([1, 9])
with col1:
    start, end, limit = settings_top_donator()
with col2:
    top_donateur_df = cache_get_top_donateurs(limit)
    display_top_donators(top_donateur_df)



col1, col2 = st.columns([1, 9])
with col1:
    start, end = settings_reglement_regulier()
with col2:
    top_donateur_reg_df = cache_get_top_donateurs_regulier(start, end, 10000)
    display_reglement_regulier(top_donateur_reg_df, start, end)

col1, col2 = st.columns([1, 9])
with col1:
    start, end, hide = settings_cause()
with col2:
    top_cause_df = cache_get_top_cause(start, end)
    display_top_cause(top_cause_df, hide)
