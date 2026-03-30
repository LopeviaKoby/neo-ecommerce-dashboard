import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery

# ── BigQuery settings (UNTOUCHED) ──
PROJECT_ID = "bussiness-case-tyc"
DATASET = "business_case_lopez_chavarria"

# ── Create API client (official Streamlit pattern) ──
# Supports both nested [gcp_service_account] and flat secrets formats
if "gcp_service_account" in st.secrets:
    _creds_info = st.secrets["gcp_service_account"]
elif "type" in st.secrets and st.secrets["type"] == "service_account":
    _creds_info = st.secrets
else:
    _creds_info = None

if _creds_info is not None:
    credentials = service_account.Credentials.from_service_account_info(
        dict(_creds_info)
    )
    _client = bigquery.Client(project=PROJECT_ID, credentials=credentials)
else:
    _client = bigquery.Client(project=PROJECT_ID)


@st.cache_data(ttl=3600)
def load_data(view_name: str) -> pd.DataFrame:
    """Carga los datos directamente desde las vistas de BigQuery."""
    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET}.{view_name}`"
    try:
        return _client.query(query).to_dataframe()
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
