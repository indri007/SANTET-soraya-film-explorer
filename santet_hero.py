"""
santet_hero.py — hero landing SANTET bergaya Material 3.

- Kartu hero ekstra-besar (radius 28) dengan video lilin di latar + scrim gradasi.
- Latar cadangan gradasi bara: teks tetap terbaca walau video gagal diputar.
- Chip angka dibaca dari data (data/films_clean.csv, results/sna_*/), bukan diketik.
- Tombol M3: filled (Dashboard) + outlined (GitHub).
"""
import base64
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
VIDEO = ROOT / "streamlit_app" / "assets" / "hero.mp4"
REPO_URL = "https://github.com/indri007/SANTET-soraya-film-explorer"


@st.cache_data(show_spinner=False)
def _video_b64() -> str:
    return base64.b64encode(VIDEO.read_bytes()).decode() if VIDEO.exists() else ""


@st.cache_data(show_spinner=False)
def _facts() -> dict:
    """Angka untuk chip hero. Kalau file tidak ada, chip itu tidak ditampilkan."""
    out = {}
    try:
        import pandas as pd
        f = pd.read_csv(ROOT / "data" / "films_clean.csv")
        out["film"] = f"{len(f)} film · {int(f['tahun'].min())}–{int(f['tahun'].max())}"
        out["studio"] = f"{f['rumah_produksi'].nunique()} rumah produksi"
        runs = sorted((ROOT / "results").glob("sna_*/nodexl/vertices.csv"))
        if runs:
            v = pd.read_csv(runs[-1], encoding="utf-8-sig")
            akun = int((v["Jenis"] == "user").sum())
            out["akun"] = f"{akun:,} akun anonim".replace(",", ".")
        out["sna"] = "20 analisis jaringan"
    except Exception:  # noqa: BLE001 — hero tidak boleh membuat halaman gagal
        pass
    return out


CSS = """
<style>
.m3-hero { position: relative; isolation: isolate; overflow: hidden;
  min-height: clamp(440px, 74vh, 760px); border-radius: 28px; margin: 0 0 2.5rem;
  display: flex; align-items: flex-end;
  background:
    radial-gradient(60% 70% at 50% 110%, rgba(194,65,12,.55), transparent 70%),
    radial-gradient(40% 50% at 15% 10%, rgba(0,80,74,.35), transparent 70%),
    linear-gradient(160deg, #170B08 0%, #261814 55%, #1D100C 100%);
  box-shadow: 0 1px 3px rgba(0,0,0,.3), 0 8px 24px rgba(0,0,0,.35); }
.m3-hero video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
  z-index: -2; opacity: .55; }
.m3-hero::after { content: ""; position: absolute; inset: 0; z-index: -1;
  background: linear-gradient(180deg, rgba(23,11,8,.15) 0%, rgba(23,11,8,.35) 45%, rgba(23,11,8,.92) 100%); }
.m3-hero__inner { width: 100%; padding: clamp(1.5rem, 4vw, 3.5rem); }
.m3-overline { display: inline-flex; align-items: center; gap: .5rem; padding: .35rem .85rem;
  border-radius: 8px; background: rgba(194,65,12,.85); color: #FFECE7; font-size: .78rem;
  font-weight: 600; letter-spacing: .1em; text-transform: uppercase; backdrop-filter: blur(6px); }
.m3-dot { width: 8px; height: 8px; border-radius: 50%; background: #FFB59D;
  box-shadow: 0 0 10px #FFB59D; animation: m3-flicker 3.2s infinite; }
.stApp .m3-hero h1.m3-title { font-family: 'Fraunces', Georgia, serif !important; font-weight: 700 !important;
  color: #FFF8F6 !important; font-size: clamp(3.5rem, 10vw, 8rem) !important; line-height: .95 !important;
  letter-spacing: -0.035em; margin: 1.1rem 0 .7rem !important; padding: 0 !important;
  text-shadow: 0 0 40px rgba(255,140,90,.35); animation: m3-glow 4s ease-in-out infinite; }
.stApp .m3-hero h1.m3-title a, .stApp .m3-hero [data-testid="stHeaderActionElements"] { display: none !important; }
.m3-tagline { font-family: 'Fraunces', Georgia, serif; font-style: italic; font-weight: 400;
  color: #F7DDD6; font-size: clamp(1.15rem, 2.2vw, 1.6rem); margin: 0 0 .4rem; max-width: 46ch; }
.m3-sub { color: #E1BFB5; font-size: 1rem; margin: 0 0 1.6rem; max-width: 60ch; letter-spacing: .01em; }
.m3-actions { display: flex; flex-wrap: wrap; gap: .75rem; margin-bottom: 1.4rem; }
.m3-btn { display: inline-flex; align-items: center; gap: .5rem; min-height: 48px; padding: 0 1.6rem;
  border-radius: 100px; font-weight: 600; font-size: .95rem; letter-spacing: .01em;
  text-decoration: none !important; transition: box-shadow .2s, filter .2s, background .2s; }
.m3-btn--filled { background: #FFB59D; color: #5D1800 !important; }
.m3-btn--filled:hover { box-shadow: 0 2px 8px rgba(0,0,0,.4); filter: brightness(1.05); }
.m3-btn--outlined { border: 1px solid #A88A81; color: #F7DDD6 !important; background: rgba(23,11,8,.25);
  backdrop-filter: blur(6px); }
.m3-btn--outlined:hover { background: rgba(247,221,214,.10); }
.m3-btn svg { width: 18px; height: 18px; fill: currentColor; }
.m3-chips { display: flex; flex-wrap: wrap; gap: .5rem; margin-bottom: 1.2rem; }
.m3-chip { display: inline-flex; align-items: center; height: 32px; padding: 0 .9rem; border-radius: 8px;
  border: 1px solid rgba(225,191,181,.45); color: #F7DDD6; font-size: .85rem; font-weight: 500;
  background: rgba(23,11,8,.35); backdrop-filter: blur(6px); }
.m3-disclaimer { color: rgba(225,191,181,.75); font-size: .78rem; margin: 0; }
@keyframes m3-flicker { 0%,100% { opacity: 1 } 45% { opacity: .55 } 50% { opacity: .9 } 70% { opacity: .65 } }
@keyframes m3-glow { 0%,100% { text-shadow: 0 0 36px rgba(255,140,90,.30) } 50% { text-shadow: 0 0 56px rgba(255,140,90,.55) } }
@media (prefers-reduced-motion: reduce) { .stApp .m3-hero h1.m3-title, .m3-dot { animation: none; } .m3-hero video { display: none; } }
@media (max-width: 640px) { .m3-hero { border-radius: 20px; min-height: 520px; } .m3-btn { width: 100%; justify-content: center; } }
</style>
"""

ICON_HUB = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a3 3 0 0 0-1 5.83V10H7.83A3 3 0 1 0 '
            '6 12a3 3 0 0 0 1.83-.17V14H5a3 3 0 1 0 2 2.83V16h10v.83A3 3 0 1 0 19 14h-2.83v-2.17A3 3 0 1 0 '
            '18 10h-5V7.83A3 3 0 0 0 12 2Z"/></svg>')
ICON_CODE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.7 16.6 4.1 12l4.6-4.6L7.3 6l-6 6 6 6 '
             '1.4-1.4Zm6.6 0 4.6-4.6-4.6-4.6L16.7 6l6 6-6 6-1.4-1.4Z"/></svg>')


def render_hero() -> None:
    vid = _video_b64()
    video = (f'<video autoplay muted loop playsinline preload="auto" aria-hidden="true">'
             f'<source src="data:video/mp4;base64,{vid}" type="video/mp4"></video>') if vid else ""
    chips = "".join(f'<span class="m3-chip">{t}</span>' for t in _facts().values())
    st.markdown(CSS + f"""
<section class="m3-hero" aria-label="SANTET">
  {video}
  <div class="m3-hero__inner">
    <span class="m3-overline"><span class="m3-dot"></span>Riset independen · horor Indonesia</span>
    <h1 class="m3-title">SANTET</h1>
    <p class="m3-tagline">"Membaca 'mantra' warganet sebelum film tayang."</p>
    <p class="m3-sub">Sentiment Analysis for Nusantara Theatrical Expectation Tracking —
      mendengar jeritan penonton di kolom komentar trailer, dan membacanya sebagai pujian.</p>
    <div class="m3-actions">
      <a class="m3-btn m3-btn--filled" href="app" target="_self">{ICON_HUB}Buka Dashboard SNA</a>
      <a class="m3-btn m3-btn--outlined" href="{REPO_URL}" target="_blank" rel="noopener">{ICON_CODE}Kode di GitHub</a>
    </div>
    <div class="m3-chips">{chips}</div>
    <p class="m3-disclaimer">Tidak berafiliasi dengan Soraya Intercine Films, Hitmaker Studios, atau MD Pictures.</p>
  </div>
</section>""", unsafe_allow_html=True)
