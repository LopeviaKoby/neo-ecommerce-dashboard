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
    if "gcp_service_account" in st.secrets:
        credentials = service_account.Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"])
        )
        return bigquery.Client(project=PROJECT_ID, credentials=credentials)
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


def load_all() -> dict[str, pd.DataFrame]:
    """Load every view used by the dashboard. Returns a dict keyed by short name."""
    return {
        "top_prod":  load_data("vw_top_productos_categoria"),
        "clientes":  load_data("vw_comportamiento_clientes"),
        "logistica": load_data("vw_tiempos_logistica"),
        "stock":     load_data("vw_inventario_reabastecimiento"),
    }
