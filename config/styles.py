import streamlit as st
from config.palette import (
    PRIMARY, ACCENT, LIGHT, BG_CARD, BG_PAGE,
    TEXT_DARK, TEXT_MUTED,
)


def inject_css() -> None:
    """Inject the global CSS for the Control Room theme."""
    st.markdown(f"""
    <style>
        /* ── Page background ── */
        .stApp {{
            background-color: {BG_PAGE};
        }}
        /* ── Header bar ── */
        .dashboard-header {{
            background: linear-gradient(135deg, {PRIMARY} 0%, {ACCENT} 100%);
            padding: 1.8rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.2rem;
            color: white;
        }}
        .dashboard-header h1 {{
            margin: 0; font-size: 1.65rem; font-weight: 700; letter-spacing: .3px;
        }}
        .dashboard-header p {{
            margin: .35rem 0 0 0; font-size: .92rem; opacity: .85;
        }}
        /* ── KPI cards ── */
        .kpi-card {{
            background: {BG_CARD};
            border-radius: 12px;
            padding: 1.25rem 1.4rem;
            box-shadow: 0 1px 4px rgba(0,0,0,.06), 0 4px 12px rgba(0,0,0,.04);
            border-left: 4px solid {ACCENT};
            transition: transform .15s ease, box-shadow .15s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,.10);
        }}
        .kpi-label {{
            font-size: .78rem; color: {TEXT_MUTED}; text-transform: uppercase;
            letter-spacing: .6px; margin-bottom: .3rem; font-weight: 600;
        }}
        .kpi-value {{
            font-size: 1.7rem; font-weight: 700; color: {TEXT_DARK}; line-height: 1.2;
        }}
        /* ── Product cards ── */
        .product-card {{
            background: {BG_CARD};
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 1px 4px rgba(0,0,0,.06), 0 4px 12px rgba(0,0,0,.04);
            transition: transform .15s ease, box-shadow .15s ease;
            height: 100%;
        }}
        .product-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,.10);
        }}
        .product-card img {{
            border-radius: 10px;
            margin-bottom: .6rem;
            width: 80px; height: 80px; object-fit: cover;
        }}
        .product-name {{
            font-size: .78rem; font-weight: 600; color: {TEXT_DARK};
            line-height: 1.25; margin-bottom: .35rem;
            display: -webkit-box; -webkit-line-clamp: 2;
            -webkit-box-orient: vertical; overflow: hidden;
            min-height: 2rem;
        }}
        .product-qty {{
            font-size: 1.1rem; font-weight: 700; color: {ACCENT};
        }}
        .product-category {{
            font-size: .68rem; color: {TEXT_MUTED}; margin-top: .2rem;
        }}
        /* ── Section titles ── */
        .section-title {{
            font-size: 1.05rem; font-weight: 700; color: {PRIMARY};
            margin: 1.2rem 0 .6rem 0; padding-bottom: .3rem;
            border-bottom: 2px solid {ACCENT};
            display: inline-block;
        }}
        /* ── Sidebar styling ── */
        section[data-testid="stSidebar"] {{
            background-color: {BG_CARD};
        }}
        /* ── Hide default streamlit header spacing ── */
        .block-container {{
            padding-top: 1rem;
        }}
        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            padding: .6rem 1.5rem;
            font-weight: 600;
        }}
    </style>
    """, unsafe_allow_html=True)
