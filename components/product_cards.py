import base64
from pathlib import Path
import streamlit as st
import pandas as pd
from config.palette import PRIMARY, ACCENT

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "products"


def _load_image_b64(filename: str) -> str | None:
    """Load a local image as a base64 data URI. Returns None if not found."""
    path = _ASSETS_DIR / filename
    if not path.exists():
        return None
    suffix = path.suffix.lower()
    mime = {".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}.get(suffix, "image/webp")
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def _fallback_svg(name: str) -> str:
    """Inline SVG avatar as fallback when no local image exists."""
    words = name.split()
    initials = (words[0][0] + (words[1][0] if len(words) > 1 else "")).upper()
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80">'
        f'<rect width="80" height="80" rx="40" fill="{PRIMARY}"/>'
        f'<text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" '
        f'font-family="sans-serif" font-size="26" font-weight="700" fill="#fff">'
        f'{initials}</text></svg>'
    )
    b64 = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"


def render_product_cards(df_top: pd.DataFrame, n: int = 5) -> None:
    """Render the top-N products as visual cards.

    Image resolution order:
      1. Local file in assets/products/<index>.webp  (e.g. 1.webp, 2.webp …)
      2. Inline SVG fallback with initials
    """
    top = df_top.head(n)
    cols = st.columns(n)
    for i, (_, row) in enumerate(top.iterrows()):
        nombre = row["nombre_producto"]
        # Try local image first (1.webp, 2.webp, etc.)
        img_src = None
        for ext in (".webp", ".png", ".jpg"):
            img_src = _load_image_b64(f"{i + 1}{ext}")
            if img_src:
                break
        if not img_src:
            img_src = _fallback_svg(nombre)

        with cols[i]:
            st.markdown(
                f"""
                <div class="product-card">
                    <img src="{img_src}" alt="{nombre[:30]}">
                    <div class="product-name">{nombre}</div>
                    <div class="product-qty">{int(row['cantidad_vendida'])} uds.</div>
                    <div class="product-category">{row['categoria_producto']}</div>
                </div>""",
                unsafe_allow_html=True,
            )
