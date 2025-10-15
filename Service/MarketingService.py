import snowflake.connector
import streamlit as st
import pandas as pd
import os
from Model.interval import Interval
from datetime import date

# For dev only, will crash prod
# from dotenv import load_dotenv
# load_dotenv()

class MarketingService():
    def __init__(self):
        self.conn = st.connection("snowflake")
        self.cur = self.conn.cursor()

    def _execute_and_return_query(self, query):
        self.cur.execute(query)
        rows = self.cur.fetchall()
        col_names = [desc[0] for desc in self.cur.description]
        df = pd.DataFrame(rows, columns=col_names)
        return df
    

    def get_reglement_regulier(self, interval: Interval, start: date, end: date, agg: bool) -> pd.DataFrame:
        # Validate interval -> values accepted by DATE_TRUNC in Snowflake
        mapping = {
            Interval.YEAR:  ("year",  "YYYY"),
            Interval.MONTH: ("month", "YYYY-MM"),
            Interval.DAY:   ("day",   "YYYY-MM-DD"),
        }

        if interval not in mapping:
            raise ValueError(f"Unsupported interval: {interval}")

        date_trunc, label_fmt = mapping[interval]

        # Format dates as ISO strings for safe embedding (we validated earlier)
        start_str = start.isoformat()   # 'YYYY-MM-DD'
        end_str = end.isoformat()

        # Build base query
        query = f"""
        WITH filtered AS (
        SELECT
            TO_DATE(DATEREGLEMENT, 'YYYYMMDD') AS reg_date,
            MONTANTREGLEMENT
        FROM REGLEMENTPONCTUEL
        WHERE TO_DATE(DATEREGLEMENT, 'YYYYMMDD') 
            BETWEEN TO_DATE('{start_str}', 'YYYY-MM-DD') AND TO_DATE('{end_str}', 'YYYY-MM-DD')
        ),
        agg AS (
        SELECT
            DATE_TRUNC('{date_trunc}', reg_date) AS period_date,
            TO_CHAR(DATE_TRUNC('{date_trunc}', reg_date), '{label_fmt}') AS period_label,
            SUM(MONTANTREGLEMENT) AS total_amount
        FROM filtered
        GROUP BY DATE_TRUNC('{date_trunc}', reg_date)
        )
        """

        if agg:
            # Include running sum (cumulative total)
            query += """
        SELECT
        period_label AS PERIOD,
        total_amount AS TOTAL_MONTANTREGLEMENT,
        SUM(total_amount) OVER (ORDER BY period_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            AS CUMULATIVE_TOTAL_MONTANTREGLEMENT
        FROM agg
        ORDER BY period_date;
        """
        else:
            query += """
        SELECT
        period_label AS PERIOD,
        total_amount AS TOTAL_MONTANTREGLEMENT
        FROM agg
        ORDER BY period_date;
        """

        # Execute
        self.cur.execute(query)
        rows = self.cur.fetchall()
        col_names = [desc[0] for desc in self.cur.description]
        df = pd.DataFrame(rows, columns=col_names)

        # Optional: if INTERVAL = YEAR filter out out-of-range years (example from before)
        if interval == Interval.YEAR and "PERIOD" in df.columns:
            # PERIOD is a string like '2005' or '2024'
            try:
                df["PERIOD"] = df["PERIOD"].astype(int)
                today = date.today()
                df = df[(df["PERIOD"] >= 2000) & (df["PERIOD"] <= today.year)]
            except Exception:
                # keep original if cast fails
                pass

        return df
    
    def get_top_donateurs(self, top: int):
        query = f"""
        SELECT 
            e.IDINDIVIDU,
            e.NOM,
            e.PRENOM,
            SUM(CAST(r.MONTANT AS FLOAT)) AS total_dons
        FROM 
            WAREHOUSE_DB.SCHEMA.RECUFISCAL r
        JOIN 
            WAREHOUSE_DB.SCHEMA.ENVOISRECUFISCAL e 
            ON r.IDRECUFISCAL = e.IDRECUFISCAL
        WHERE CAST(r.MONTANT AS FLOAT) > 1000
        GROUP BY 
            e.IDINDIVIDU, e.NOM, e.PRENOM
        ORDER BY 
            total_dons DESC
        LIMIT {top};
        """
        return self._execute_and_return_query(query)
    
    def get_top_donateurs_regulier(self, start: date, end: date, top: int):
        # start_str = start.isoformat()
        # end_str = end.isoformat()
        query = """
        SELECT * 
        FROM REGLEMENTREGULIER
        """
        # WHERE TO_DATE(DATEDEMANDE, 'YYYYMMDD') BETWEEN 
        # TO_DATE('{start_str}', 'YYYY-MM-DD') AND TO_DATE('{end_str}', 'YYYY-MM-DD')
        # OR TO_DATE(DATEANNULATION, 'YYYYMMDD') BETWEEN 
        # TO_DATE('{start_str}', 'YYYY-MM-DD') AND TO_DATE('{end_str}', 'YYYY-MM-DD')
        # LIMIT {top}
        return self._execute_and_return_query(query)
    
    def get_top_cause(self, start, end):
        start_str = start.strftime("%Y%m%d")
        end_str = end.strftime("%Y%m%d")
        query = f"""
        SELECT 
            c.LIBCAUSE AS cause_name,
            d.IDCAUSE,
            SUM(CAST(r.montant AS FLOAT)) AS total_dons
        FROM 
            WAREHOUSE_DB.SCHEMA.DONPONCTUEL d
        
        JOIN 
            WAREHOUSE_DB.SCHEMA.RECUFISCAL r 
            ON d.IDRECUFISCAL = r.IDRECUFISCAL
        JOIN 
            WAREHOUSE_DB.SCHEMA.CAUSE_OEUVRE c 
            ON d.IDCAUSE = c.IDCAUSE
        WHERE d.DATEDON BETWEEN {start_str} AND {end_str}
        GROUP BY 
            c.LIBCAUSE, d.IDCAUSE
        ORDER BY 
            total_dons DESC;
        """
        return self._execute_and_return_query(query)

ms = MarketingService()

@st.cache_data(ttl=60*60)
def cache_get_reglement_regulier(interval: Interval, start: date, end: date, agg: bool):
    return ms.get_reglement_regulier(interval, start, end, agg)

@st.cache_data(ttl=60*60)
def cache_get_top_donateurs(top: int):
    return ms.get_top_donateurs(top)

@st.cache_data(ttl=60*60)
def cache_get_top_donateurs_regulier(start: date, end: date, top: int):
    return ms.get_top_donateurs_regulier(start, end, top)

@st.cache_data(ttl=60*60)
def cache_get_top_cause(start, end):
    return ms.get_top_cause(start, end)