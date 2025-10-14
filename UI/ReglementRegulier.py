import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
from pandas.tseries.offsets import DateOffset


import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculer_prelevements_mensuels(df, start: date, end: date):
    """
    Calcule la somme des prélèvements par mois
    
    Paramètres:
    - df: DataFrame avec les colonnes DATEPREMIERPREL/DATEDEMANDE, 
          DATEFINPREL/DATEANNULATION, frequence et montant
    - colonne_montant: nom de la colonne contenant le montant du prélèvement
    """
    
    # Identifier les colonnes de date
    col_debut = 'DATEPREMIERPREL' if 'DATEPREMIERPREL' in df.columns else 'DATEDEMANDE'
    col_fin = 'DATEANNULATION'
    
    # Convertir les dates du format YYYYMMDD en datetime
    df['date_debut'] = pd.to_datetime(df[col_debut], format='%Y%m%d', errors='coerce')
    df['date_fin'] = pd.to_datetime(df[col_fin], format='%Y%m%d', errors='coerce')
    df['frequence'] = pd.to_numeric(df["IDFREQUENCEPREL"], errors="coerce").fillna(0).astype(int)
    df['montant'] = pd.to_numeric(df["MONTANTPREL"], errors="coerce").fillna(0).astype(int)
    
    # Liste pour stocker tous les prélèvements mensuels
    prelevements_mensuels = []
    
    # Parcourir chaque ligne du dataframe
    for idx, row in df.iterrows():
        date_debut = row['date_debut']
        date_fin = row['date_fin']
        frequence = row['frequence']
        montant = row['montant']
        
        # Ignorer les lignes avec des dates invalides
        if pd.isna(date_debut):
            continue
        
        # Si pas de date de fin, utiliser une date lointaine (par exemple 10 ans)
        if pd.isna(date_fin):
            date_fin = date_debut + relativedelta(years=10)
        
        # Générer les dates de prélèvement selon la fréquence
        if frequence == 0:
            # Prélèvement ponctuel : une seule fois à la date de début
            mois = date_debut.strftime('%Y-%m')
            prelevements_mensuels.append({'mois': mois, 'montant': montant})
        
        else:
            # Prélèvements réguliers
            date_courante = date_debut
            intervalle_mois = frequence
            
            # Générer toutes les occurrences
            while date_courante <= date_fin:
                mois = date_courante.strftime('%Y-%m')
                prelevements_mensuels.append({'mois': mois, 'montant': montant})
                date_courante = date_courante + relativedelta(months=intervalle_mois)
    
    # Créer un DataFrame et agréger par mois
    df_mensuels = pd.DataFrame(prelevements_mensuels)
    
    if len(df_mensuels) > 0:
        resultat = df_mensuels.groupby('mois')['montant'].sum().reset_index()
        resultat.columns = ['mois', 'total_prelevements']
        resultat = resultat.sort_values('mois')
    else:
        resultat = pd.DataFrame(columns=['mois', 'total_prelevements'])
    
    resultat["datetime"] = pd.to_datetime(resultat["mois"], format="%Y-%m")

    # Apply the filter — note: use "&" not "and"
    resultat = resultat[
        (resultat["datetime"] >= pd.to_datetime(start)) &
        (resultat["datetime"] <= pd.to_datetime(end))
    ]
    resultat.drop("datetime", axis=1, inplace=True)
 
    return resultat


def settings_reglement_regulier():
    st.subheader("Paramètres")
    start = st.date_input(
        "Début",
        value=date.today() - relativedelta(years=1),
        min_value=date(2000, 1, 1),
        max_value=date.today(),
        key=2
    )
    end = st.date_input(
        "Fin",
        value=date.today(),
        min_value=date(2000, 1, 1),
        max_value=date.today(),
        key=3
    )
    return start, end

def display_reglement_regulier(df, start, end):
    st.subheader("🗓️ Don régulier")
    month_df = calculer_prelevements_mensuels(df, start, end)
    st.dataframe(month_df)
    st.bar_chart(
        data=month_df,
        x="mois",
        y="total_prelevements",
    )
