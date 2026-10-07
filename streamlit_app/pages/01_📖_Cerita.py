import base64
from pathlib import Path
import streamlit as st

VIDEO = Path(__file__).resolve().parents[1] / "assets" / "hero.mp4"

def hero():
    if not VIDEO.exists():
        st.title("🕯️ SANTET")
        st.caption("The Scream Is a Compliment")
        return
    b64 = base64.b64encode(VIDEO.read_bytes()).decode()
    st.markdown(f"""
<div style="position:relative;height:70vh;overflow:hidden;border-radius:16px;margin-bottom:2rem">
  <video autoplay muted loop playsinline
    style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(.4)">
    <source src="data:video/mp4;base64,{b64}" type="video/mp4"></video>
  <div style="position:relative;z-index:1;height:100%;display:flex;flex-direction:column;
    justify-content:center;align-items:center;color:#fff;text-align:center;padding:0 16px">
    <h1 style="font-size:clamp(2rem,6vw,3.5rem);margin:0">🕯️ SANTET</h1>
    <p style="font-size:1.2rem;opacity:.9">The Scream Is a Compliment</p>
    <p style="font-size:.95rem;opacity:.7;max-width:640px">
      Sentiment Analysis for Nusantara Theatrical Expectation Tracking</p>
  </div>
</div>""", unsafe_allow_html=True)

hero()

st.markdown("""
### Tentang riset ini
Analisis jaringan dan sentimen percakapan YouTube seputar film horor Soraya Intercine Films dan MD Pictures.
""")

if (Path(__file__).resolve().parents[1] / "app.py").exists():
    st.page_link("streamlit_app/app.py", label="Buka Dashboard jaringan (SNA)", icon="🕸️")
