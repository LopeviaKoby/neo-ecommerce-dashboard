import streamlit as st

from config.styles import inject_css
from data.loader import load_all
from tabs import comercial, logistica

# ── Page config (MUST be the first st.* call) ──
st.set_page_config(
    page_title="Neo E-Commerce | Control Room",
    page_icon="https://ui-avatars.com/api/?name=Neo&background=1B3A5C&color=fff&size=32",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme ──
inject_css()

# ── Header ──
st.markdown("""
<div class="dashboard-header">
    <h1>Neo E-Commerce &middot; Control Room</h1>
    <p>Vision integral del rendimiento comercial y eficiencia operativa de la red logistica</p>
</div>
""", unsafe_allow_html=True)

# ── DEBUG: remove after confirming secrets work ──
st.caption(f"Secrets keys: {list(st.secrets.keys())}")

# ── Data ──
with st.spinner("Cargando metricas de negocio..."):
    data = load_all()

# ── Sidebar filter ──
with st.sidebar:
    st.markdown("### Filtros")
    centros = ["Todos"]
    if not data["logistica"].empty:
        centros += sorted(data["logistica"]["nombre_centro"].unique().tolist())
    filtro_centro = st.selectbox(
        "Centro de Distribucion",
        centros,
        index=0,
        help="Filtra el mapa y metricas logisticas por centro",
    )

# ── Tabs ──
tab_com, tab_log = st.tabs(
    ["Analisis Comercial y Marketing", "Optimizacion Logistica"]
)

with tab_com:
    comercial.render(data["clientes"], data["top_prod"])

with tab_log:
    logistica.render(data["logistica"], data["stock"], filtro_centro)
