import streamlit as st
import pandas as pd
import plotly.express as px

from config.palette import PRIMARY, ACCENT, LIGHT, SUCCESS
from components.kpi import kpi_card, format_number
from components.product_cards import render_product_cards

# Shared Plotly config: hide toolbar for clean Control Room look
_PLOTLY_CFG = {"displayModeBar": False}


def render(df_clientes: pd.DataFrame, df_top_prod: pd.DataFrame) -> None:
    """Render the full Commercial & Marketing tab."""
    if df_clientes.empty or df_top_prod.empty:
        st.warning("No hay datos comerciales disponibles.")
        return

    # ── KPI Row ──
    st.markdown(
        '<div class="section-title">Metricas Generales de Clientes</div>',
        unsafe_allow_html=True,
    )
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card(
            "Total Clientes",
            format_number(df_clientes["frecuencia_compra"].count()),
        )
    with k2:
        kpi_card(
            "Ticket Medio Global",
            f"${df_clientes['ticket_medio'].mean():.2f}",
            LIGHT,
        )
    with k3:
        kpi_card(
            "Gasto Total Acumulado",
            format_number(df_clientes["total_gastado"].sum(), prefix="$"),
            SUCCESS,
        )
    with k4:
        kpi_card(
            "Recencia Promedio (Meses)",
            f"{df_clientes['recencia_meses'].mean():.1f}",
            PRIMARY,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top 5 Products as Visual Cards ──
    st.markdown(
        '<div class="section-title">Top 5 Productos Mas Vendidos</div>',
        unsafe_allow_html=True,
    )
    render_product_cards(df_top_prod, n=5)

    # ── Expander: full product table ──
    with st.expander("Ver listado completo de demanda por categoria"):
        df_table = df_top_prod[["nombre_producto", "categoria_producto", "cantidad_vendida"]].copy()
        df_table.columns = ["Producto", "Categoria", "Unidades Vendidas"]
        st.dataframe(
            df_table.style.format({"Unidades Vendidas": "{:,.0f}"}),
            hide_index=True,
            use_container_width=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Demographics chart (full width) ──
    st.markdown(
        '<div class="section-title">Comportamiento de Gasto por Genero y Edad</div>',
        unsafe_allow_html=True,
    )
    df_demo = df_clientes.dropna(subset=["edad", "ticket_medio"])
    fig_demo = px.scatter(
        df_demo,
        x="edad",
        y="ticket_medio",
        color="genero",
        opacity=0.5,
        labels={
            "edad": "Edad del Cliente",
            "ticket_medio": "Ticket Medio ($)",
            "genero": "Genero",
        },
        color_discrete_map={"M": ACCENT, "F": LIGHT},
    )
    fig_demo.update_traces(
        hovertemplate="Edad: %{x}<br>Ticket Medio: $%{y:,.2f}<extra></extra>",
    )
    fig_demo.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=20, t=10, b=40),
        font=dict(size=11),
    )
    st.plotly_chart(fig_demo, use_container_width=True, config=_PLOTLY_CFG)
