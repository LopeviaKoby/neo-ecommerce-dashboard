from concurrent.futures import ThreadPoolExecutor

import streamlit as st
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# ── BigQuery settings (UNTOUCHED) ──
PROJECT_ID = "bussiness-case-tyc"
DATASET = "business_case_lopez_chavarria"


@st.cache_resource
def _get_client() -> bigquery.Client:
    """BigQuery client (cached singleton): uses st.secrets on Streamlit Cloud, ADC elsewhere."""
    try:
        creds_info = st.secrets["gcp_service_account"]
        credentials = service_account.Credentials.from_service_account_info(
            dict(creds_info)
        )
        return bigquery.Client(project=PROJECT_ID, credentials=credentials)
    except (KeyError, FileNotFoundError):
        return bigquery.Client(project=PROJECT_ID)


@st.cache_data(ttl=3600)
def load_data(view_name: str) -> pd.DataFrame:
    """Carga los datos directamente desde las vistas de BigQuery."""
    client = _get_client()
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
    """Load all views. Uses threads on non-cloud envs, sequential on Streamlit Cloud."""
    try:
        # If st.secrets has credentials, we're on Streamlit Cloud — load sequentially
        # to avoid thread issues with st.cache_data
        _ = st.secrets["gcp_service_account"]
        return {key: load_data(view) for key, view in _VIEWS.items()}
    except (KeyError, FileNotFoundError):
        # Local / Cloud Run — parallel is safe
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {key: pool.submit(load_data, view) for key, view in _VIEWS.items()}
            return {key: fut.result() for key, fut in futures.items()}
