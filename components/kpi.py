import streamlit as st
from config.palette import ACCENT


def format_number(n: float, prefix: str = "", suffix: str = "") -> str:
    """Human-friendly abbreviation: 8046620 -> '$8.0M', 66169 -> '66.2K'."""
    abs_n = abs(n)
    if abs_n >= 1_000_000:
        short = f"{n / 1_000_000:.1f}M"
    elif abs_n >= 1_000:
        short = f"{n / 1_000:.1f}K"
    else:
        short = f"{n:,.0f}"
    return f"{prefix}{short}{suffix}"


def kpi_card(label: str, value: str, border_color: str = ACCENT) -> None:
    """Render a styled KPI card via HTML injection."""
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left-color:{border_color}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>""",
        unsafe_allow_html=True,
    )
