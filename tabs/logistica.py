import streamlit as st
import pandas as pd
import plotly.express as px

from config.palette import PRIMARY, ACCENT, LIGHT, SUCCESS, DANGER
from components.kpi import kpi_card

# Human-readable legend names for raw column names
_LEGEND_RENAME = {
    "avg_horas_procesamiento": "Procesamiento",
    "avg_horas_entrega": "Entrega",
    "stock_disponible": "Stock Disponible",
    "demanda_historica": "Demanda Historica",
}

# Shared Plotly config: hide toolbar for clean Control Room look
_PLOTLY_CFG = {"displayModeBar": False}


def render(
    df_logistica: pd.DataFrame,
    df_stock: pd.DataFrame,
    filtro_centro: str,
) -> None:
    """Render the full Logistics Optimization tab."""
    if df_logistica.empty or df_stock.empty:
        st.warning("No hay datos logisticos disponibles.")
        return

    # ── Apply center filter ──
    if filtro_centro != "Todos":
        df_log = df_logistica[df_logistica["nombre_centro"] == filtro_centro]
    else:
        df_log = df_logistica

    # ── Logistics KPIs ──
    st.markdown(
        '<div class="section-title">Red de Distribucion</div>',
        unsafe_allow_html=True,
    )
    lk1, lk2, lk3 = st.columns(3)
    with lk1:
        kpi_card("Centros Activos", str(df_log["nombre_centro"].nunique()))
    with lk2:
        kpi_card("Entrega Promedio", f"{df_log['avg_horas_entrega'].mean():.1f} hrs", LIGHT)
    with lk3:
        kpi_card("Procesamiento Promedio", f"{df_log['avg_horas_procesamiento'].mean():.1f} hrs", PRIMARY)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Central Map ──
    _render_map(df_log)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Performance chart + Ranking ──
    _render_performance(df_log, df_logistica)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stock Alerts ──
    _render_stock_alerts(df_stock)


# ── Private helpers ──────────────────────────────────────────


def _render_map(df_log: pd.DataFrame) -> None:
    st.markdown(
        '<div class="section-title">Mapa de Centros de Distribucion</div>',
        unsafe_allow_html=True,
    )

    if "latitud" not in df_log.columns or "longitud" not in df_log.columns:
        st.warning(
            "La vista `vw_tiempos_logistica` no expone las columnas `latitud`/`longitud`. "
            "Asegurate de incluir `dc.latitude AS latitud, dc.longitude AS longitud` "
            "en el SELECT final del JOIN con `distribution_centers`."
        )
        return

    df_map = df_log.dropna(subset=["latitud", "longitud"]).copy()
    if df_map.empty:
        st.info("No hay coordenadas disponibles para el filtro seleccionado.")
        return

    df_map["size_metric"] = df_map["avg_horas_entrega"].fillna(1)

    fig = px.scatter_mapbox(
        df_map,
        lat="latitud",
        lon="longitud",
        hover_name="nombre_centro",
        hover_data={
            "avg_horas_entrega": False,
            "avg_horas_procesamiento": False,
            "ranking_rapidez": False,
            "latitud": False,
            "longitud": False,
            "size_metric": False,
        },
        size="size_metric",
        size_max=18,
        color="avg_horas_entrega",
        color_continuous_scale=[
            [0, SUCCESS],
            [0.5, "#FBBF24"],
            [1, DANGER],
        ],
        labels={
            "avg_horas_entrega": "Hrs Entrega",
        },
        zoom=3.5,
        center={"lat": 34.0, "lon": -95.0},
        mapbox_style="open-street-map",
    )
    # Clean hovertemplate for map markers
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Entrega: %{marker.color:.1f} hrs<br>"
            "<extra></extra>"
        ),
    )
    fig.update_layout(
        height=460,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="Hrs Entrega", thickness=14, len=0.5),
    )
    st.plotly_chart(fig, use_container_width=True, config=_PLOTLY_CFG)


def _render_performance(df_log: pd.DataFrame, df_logistica_full: pd.DataFrame) -> None:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            '<div class="section-title">Tiempos de Procesamiento vs Entrega</div>',
            unsafe_allow_html=True,
        )
        # Melt to long format so we control legend labels cleanly
        df_melted = df_log.melt(
            id_vars=["nombre_centro"],
            value_vars=["avg_horas_procesamiento", "avg_horas_entrega"],
            var_name="etapa",
            value_name="horas",
        )
        df_melted["etapa"] = df_melted["etapa"].map(_LEGEND_RENAME)

        fig = px.bar(
            df_melted,
            x="nombre_centro",
            y="horas",
            color="etapa",
            barmode="group",
            labels={
                "horas": "Horas Promedio",
                "nombre_centro": "",
                "etapa": "Etapa",
            },
            color_discrete_map={
                "Procesamiento": ACCENT,
                "Entrega": LIGHT,
            },
        )
        # Clean hover: show center name, stage and hours
        fig.update_traces(
            hovertemplate="%{x}<br>%{data.name}: %{y:.1f} hrs<extra></extra>",
        )
        if "avg_global_red_horas" in df_logistica_full.columns:
            promedio = df_logistica_full["avg_global_red_horas"].iloc[0]
            fig.add_hline(
                y=promedio,
                line_dash="dash",
                line_color=DANGER,
                annotation_text=f"Media Global ({promedio:.1f}h)",
                annotation_font_color=DANGER,
            )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=20, t=10, b=60),
            font=dict(size=11),
            xaxis_tickangle=-35,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True, config=_PLOTLY_CFG)

    with col2:
        st.markdown(
            '<div class="section-title">Ranking de Eficiencia en Entrega</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '**Lideres de Despacho (Ultima Milla)**',
        )
        df_rank = (
            df_log[["ranking_rapidez", "nombre_centro", "avg_horas_entrega"]]
            .sort_values("ranking_rapidez")
        )
        df_rank.columns = ["#", "Centro", "Hrs Entrega"]
        st.dataframe(
            df_rank.style.format({"Hrs Entrega": "{:.1f}"}),
            hide_index=True,
            use_container_width=True,
            height=280,
        )
        st.caption(
            "El ranking se calcula basado exclusivamente en el tiempo "
            "transcurrido desde el envio hasta la entrega final al cliente."
        )


def _render_stock_alerts(df_stock: pd.DataFrame) -> None:
    st.markdown(
        '<div class="section-title">Alertas de Reabastecimiento &mdash; Riesgo de Quiebre</div>',
        unsafe_allow_html=True,
    )
    st.caption("Productos con alta demanda historica vs stock fisico disponible.")

    df_alertas = df_stock[df_stock["ratio_alerta_stock"] >= 0.8].head(10)

    if df_alertas.empty:
        st.success("No hay alertas criticas de stock en este momento.")
        return

    # Melt for clean legend labels
    df_melted = df_alertas.melt(
        id_vars=["nombre_producto"],
        value_vars=["stock_disponible", "demanda_historica"],
        var_name="indicador",
        value_name="unidades",
    )
    df_melted["indicador"] = df_melted["indicador"].map(_LEGEND_RENAME)
    # Truncate long product names
    df_melted["producto"] = df_melted["nombre_producto"].str[:25].where(
        df_melted["nombre_producto"].str.len() <= 25,
        df_melted["nombre_producto"].str[:22] + "...",
    )

    fig = px.bar(
        df_melted,
        x="producto",
        y="unidades",
        color="indicador",
        barmode="group",
        color_discrete_map={
            "Stock Disponible": SUCCESS,
            "Demanda Historica": DANGER,
        },
        labels={
            "unidades": "Unidades",
            "producto": "",
            "indicador": "Indicador",
        },
    )
    fig.update_traces(
        hovertemplate="%{x}<br>%{data.name}: %{y:,.0f} uds.<extra></extra>",
    )
    fig.update_layout(
        xaxis_tickangle=-40,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=20, t=10, b=80),
        font=dict(size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True, config=_PLOTLY_CFG)
