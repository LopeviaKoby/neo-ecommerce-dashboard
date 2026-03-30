from concurrent.futures import ThreadPoolExecutor

import streamlit as st
import pandas as pd
from google.cloud import bigquery

# ── BigQuery settings (UNTOUCHED) ──
PROJECT_ID = "bussiness-case-tyc"
DATASET = "business_case_lopez_chavarria"


@st.cache_data(ttl=3600)
def load_data(view_name: str) -> pd.DataFrame:
    """Carga los datos directamente desde las vistas de BigQuery."""
    client = bigquery.Client(project=PROJECT_ID)
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET}.{view_name}`"
    try:
        return client.query(query).to_dataframe()
    except Exception as e:
        st.error(f"Error al cargar {view_name}: {e}")
        return pd.DataFrame()


# View name -> dict key mapping
_VIEWS = {
    "top_prod":  "vw_top_productos_categoria",
    "clientes":  "vw_comportamiento_clientes",
    "logistica": "vw_tiempos_logistica",
    "stock":     "vw_inventario_reabastecimiento",
}


def load_all() -> dict[str, pd.DataFrame]:
    """Load all views in parallel. ~4x faster on cold start."""
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {key: pool.submit(load_data, view) for key, view in _VIEWS.items()}
        return {key: fut.result() for key, fut in futures.items()}
