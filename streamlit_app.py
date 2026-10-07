"""
streamlit_app.py — Entrypoint Streamlit Community Cloud untuk SANTET.
Halaman yang filenya belum ada otomatis dilewati (tidak error).
"""
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
PAGES = ROOT / "streamlit_app"

candidates = [
    (PAGES / "pages" / "01_📖_Cerita.py", "Cerita SANTET", "🕯️"),
    (PAGES / "app.py", "Dashboard jaringan (SNA)", "🕸️"),
]
pages = [st.Page(p, title=t, icon=i, default=(n == 0))
         for n, (p, t, i) in enumerate(c for c in candidates if c[0].exists())]

if not pages:
    st.error("Belum ada halaman. Cek folder streamlit_app/.")
else:
    st.navigation(pages).run()
