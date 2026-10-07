"""
streamlit_app.py — entrypoint Streamlit Community Cloud untuk SANTET.
Router st.navigation + tema Material 3 (santet_m3.py) untuk semua halaman.
Halaman yang filenya belum ada otomatis dilewati.
"""
from pathlib import Path

import streamlit as st

from santet_m3 import apply_m3

ROOT = Path(__file__).resolve().parent
PAGES = ROOT / "streamlit_app"

candidates = [
    (PAGES / "pages" / "01_📖_Cerita.py", "Cerita SANTET", ":material/local_fire_department:"),
    (PAGES / "app.py", "Dashboard jaringan", ":material/hub:"),
]
pages = [st.Page(p, title=t, icon=i, default=(n == 0))
         for n, (p, t, i) in enumerate(c for c in candidates if c[0].exists())]

apply_m3()
if not pages:
    st.error("Belum ada halaman. Cek folder streamlit_app/.")
else:
    st.navigation(pages).run()
