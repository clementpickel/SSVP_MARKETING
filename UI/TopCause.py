import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas.tseries.offsets import DateOffset
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import numpy as np
import requests
import io
import json
import plotly.express as px

def display_map(df):
    df_cd = df[df['CAUSE_NAME'].str.startswith("CD")].copy()
    df_cd['DEP'] = df_cd['CAUSE_NAME'].str.extract(r'CD00([0-9]{2})')[0]

    dept_dons = df_cd.groupby('DEP')['TOTAL_DONS'].sum().reset_index()

    departements = gpd.read_file("assets/departements.geojson")

    departements = departements.merge(dept_dons, left_on='code', right_on='DEP', how='left')
    departements['TOTAL_DONS'] = departements['TOTAL_DONS'].fillna(0)
    
    with open("assets/departements.geojson") as f:
        geojson = json.load(f)

    # fig = px.choropleth(
    #     df_cd,
    #     geojson=geojson,
    #     locations='DEP',
    #     featureidkey="properties.code",
    #     color='TOTAL_DONS',
    #     color_continuous_scale="YlOrRd"
    # )

    # fig.update_geos(fitbounds="locations", visible=False)
    # selected = st.plotly_chart(fig, use_container_width=True)
    m = folium.Map(location=[46.6, 2.5], 
        zoom_start=6,
        min_zoom=6,       # prevent zoom out
        max_zoom=6,       # prevent zoom in
        zoom_control=False,  # hide zoom buttons
        dragging=False       # prevent panning
    )

    folium.Choropleth(
        geo_data=departements,
        name="choropleth",
        data=departements,
        columns=["code", "TOTAL_DONS"],
        key_on="feature.properties.code",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Total Dons"
    ).add_to(m)

    # Add hover tooltip
    folium.GeoJsonTooltip(
        fields=["nom", "TOTAL_DONS"],
        aliases=["Département:", "Total Dons:"],
        localize=True
    ).add_to(folium.GeoJson(departements).add_to(m))

    st.subheader("🌊 Carte des dons par département")
    st_folium(m, width=800, height=600)

def settings_cause():
    st.subheader("Paramètres")
    start = st.date_input(
        "Début",
        value=date.today() - relativedelta(years=1),
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
    display_map(df)

