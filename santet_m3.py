"""
santet_m3.py — Material 3 (Material You) untuk app Streamlit SANTET.

Skema warna gelap dibuat dari warna merek #C2410C dengan algoritme resmi Material
(materialyoucolor, SchemeFidelity): primary container = #C2410C persis.
Tertiary = teal #0F766E yang sudah dipakai di halaman Cerita.

Pakai: panggil apply_m3() sekali di streamlit_app.py sebelum nav.run().
"""
import streamlit as st

# ── token warna M3 (dark) ───────────────────────────────────────────────────
C = {
    "primary": "#FFB59D", "on-primary": "#5D1800",
    "primary-container": "#C2410C", "on-primary-container": "#FFECE7",
    "secondary": "#FFB59D", "secondary-container": "#75331C", "on-secondary-container": "#FFDBCF",
    "tertiary": "#80D5CB", "tertiary-container": "#00504A", "on-tertiary-container": "#9CF2E8",
    "error": "#FFB4AB", "error-container": "#93000A", "on-error-container": "#FFDAD6",
    "surface": "#1D100C", "surface-container-lowest": "#170B08",
    "surface-container-low": "#261814", "surface-container": "#2A1C18",
    "surface-container-high": "#352722", "surface-container-highest": "#41312C",
    "surface-bright": "#463631",
    "on-surface": "#F7DDD6", "on-surface-variant": "#E1BFB5",
    "outline": "#A88A81", "outline-variant": "#59413A",
}

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,700;1,9..144,400&"
         "family=Roboto+Flex:opsz,wght@8..144,400;8..144,500;8..144,600&display=swap")


def _vars() -> str:
    return "".join(f"--md-{k}:{v};" for k, v in C.items())


CSS = """
<style>
@import url('__FONTS__');
:root{__VARS__
  --md-font: 'Roboto Flex', system-ui, -apple-system, 'Segoe UI', sans-serif;
  --md-display: 'Fraunces', Georgia, serif;
  --md-shape-xs:4px; --md-shape-s:8px; --md-shape-m:12px; --md-shape-l:16px; --md-shape-xl:28px;
  --md-elev-1: 0 1px 2px rgba(0,0,0,.30), 0 1px 3px 1px rgba(0,0,0,.15);
  --md-elev-2: 0 1px 2px rgba(0,0,0,.30), 0 2px 6px 2px rgba(0,0,0,.15);
  --md-ease: cubic-bezier(.2,0,0,1);
}

/* ── dasar ── */
html, body, .stApp, [class*="css"], .stMarkdown, p, li, label, input, textarea, button, select {
  font-family: var(--md-font) !important; }
.stApp {
  background:
    radial-gradient(1200px 600px at 85% -10%, rgba(194,65,12,.18), transparent 60%),
    radial-gradient(900px 500px at -10% 110%, rgba(0,80,74,.18), transparent 60%),
    var(--md-surface) !important;
  color: var(--md-on-surface); }
.stApp p, .stApp li { color: var(--md-on-surface); line-height: 1.6; }
[data-testid="stCaptionContainer"], .stApp small { color: var(--md-on-surface-variant) !important; }
::selection { background: var(--md-primary-container); color: var(--md-on-primary-container); }
*:focus-visible { outline: 2px solid var(--md-primary) !important; outline-offset: 2px; }

/* ── tipografi (skala M3) ── */
.stApp h1 { font-family: var(--md-display) !important; font-weight: 700 !important;
  font-size: clamp(2rem, 4.2vw, 3.25rem) !important; line-height: 1.12 !important;
  letter-spacing: -0.02em; color: var(--md-on-surface) !important; }
.stApp h2 { font-family: var(--md-display) !important; font-weight: 500 !important;
  font-size: clamp(1.5rem, 2.6vw, 2rem) !important; line-height: 1.25 !important;
  color: var(--md-on-surface) !important; border-bottom: none !important;
  padding-bottom: .25rem !important; margin-top: 2.5rem !important; }
.stApp h3 { font-family: var(--md-font) !important; font-weight: 600 !important;
  font-size: 1.25rem !important; color: var(--md-primary) !important; }
.stApp a { color: var(--md-primary); text-decoration-thickness: 1px; text-underline-offset: 3px; }
.stApp code { background: var(--md-surface-container-highest) !important;
  color: var(--md-tertiary) !important; border-radius: 6px; padding: .1em .4em; }
.stApp hr { border-color: var(--md-outline-variant) !important; opacity: 1; }

/* ── kerangka ── */
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { right: 1rem; }
[data-testid="stMainBlockContainer"] { max-width: 1180px; padding-top: 3.5rem; }

/* ── navigation drawer ── */
[data-testid="stSidebar"] { background: var(--md-surface-container-low) !important;
  border-right: none !important; border-radius: 0 var(--md-shape-l) var(--md-shape-l) 0; }
[data-testid="stSidebar"] * { color: var(--md-on-surface-variant); }
[data-testid="stSidebarNav"] { padding: 0 .5rem; }
[data-testid="stSidebarNavLink"] { border-radius: 100px !important; min-height: 56px;
  padding: 0 1.25rem !important; margin: 2px 0; transition: background .2s var(--md-ease); }
[data-testid="stSidebarNavLink"] span { font-weight: 500; font-size: .95rem; letter-spacing: .01em; }
[data-testid="stSidebarNavLink"]:hover { background: rgba(247,221,214,.08) !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] {
  background: var(--md-secondary-container) !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] * { color: var(--md-on-secondary-container) !important;
  font-weight: 600; }
[data-testid="stSidebarNavSeparator"] { border-color: var(--md-outline-variant) !important; }

/* ── tombol: filled tonal & filled ── */
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button,
[data-testid="stBaseButton-secondary"] {
  border-radius: 100px !important; min-height: 40px; padding: 0 1.5rem !important;
  background: var(--md-secondary-container) !important; color: var(--md-on-secondary-container) !important;
  border: none !important; font-weight: 500 !important; letter-spacing: .01em;
  transition: box-shadow .2s var(--md-ease), filter .2s var(--md-ease); }
[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover,
[data-testid="stBaseButton-secondary"]:hover { box-shadow: var(--md-elev-1); filter: brightness(1.12); }
[data-testid="stPageLink"] a { display: inline-flex; align-items: center; gap: .5rem;
  border-radius: 100px; min-height: 40px; padding: 0 1.5rem;
  background: var(--md-primary) !important; text-decoration: none; }
[data-testid="stPageLink"] a * { color: var(--md-on-primary) !important; font-weight: 600; }
[data-testid="stPageLink"] a:hover { box-shadow: var(--md-elev-1); filter: brightness(1.06); }

/* ── text field (filled) ── */
[data-baseweb="select"] > div { background: var(--md-surface-container-highest) !important;
  border: none !important; border-bottom: 1px solid var(--md-on-surface-variant) !important;
  border-radius: var(--md-shape-xs) var(--md-shape-xs) 0 0 !important; }
[data-baseweb="select"] > div:focus-within { border-bottom: 2px solid var(--md-primary) !important; }
[data-testid="stWidgetLabel"] p { color: var(--md-on-surface-variant) !important; font-size: .8rem; }

/* ── tabs (primary) ── */
[data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid var(--md-outline-variant); }
[data-baseweb="tab"] { padding: .75rem 1rem !important; color: var(--md-on-surface-variant) !important; }
[data-baseweb="tab"][aria-selected="true"] { color: var(--md-primary) !important; }
[data-baseweb="tab-highlight"] { background: var(--md-primary) !important; height: 3px !important;
  border-radius: 3px 3px 0 0; }
[data-baseweb="tab-border"] { display: none; }

/* ── kartu: expander, alert, dataframe, gambar, grafik ── */
[data-testid="stExpander"] details { border: 1px solid var(--md-outline-variant) !important;
  border-radius: var(--md-shape-m) !important; background: var(--md-surface-container-low); }
[data-testid="stExpander"] summary:hover { background: rgba(247,221,214,.06); }
[data-testid="stAlertContainer"] { border-radius: var(--md-shape-m) !important; border: none !important;
  background: var(--md-surface-container-high) !important; }
[data-testid="stAlertContainer"] * { color: var(--md-on-surface-variant) !important; }
[data-testid="stDataFrame"] { border-radius: var(--md-shape-m); overflow: hidden;
  border: 1px solid var(--md-outline-variant); }
[data-testid="stImage"] img { border-radius: var(--md-shape-l); }
[data-testid="stVegaLiteChart"] { background: var(--md-surface-container-low); border-radius: var(--md-shape-l);
  padding: 1rem; }

/* ── halaman Cerita: kelas lama → komponen M3 ── */
.stat-trio { gap: 12px !important; }
.stat-box { background: var(--md-surface-container-high) !important; border: none !important;
  border-radius: var(--md-shape-l) !important; padding: 1.25rem 1.25rem 1rem !important;
  transition: transform .25s var(--md-ease), box-shadow .25s var(--md-ease); }
.stat-box:hover { transform: translateY(-2px); box-shadow: var(--md-elev-2); }
.stat-val { font-family: var(--md-display) !important; font-weight: 700 !important;
  font-size: 2.25rem !important; color: var(--md-primary) !important; line-height: 1.1; }
.stat-lbl { color: var(--md-on-surface-variant) !important; font-size: .85rem !important; margin-top: 6px !important; }
.act { background: var(--md-surface-container-low) !important; border: none !important;
  border-radius: var(--md-shape-xl) !important; padding: 2rem 2.25rem !important; margin: 1.25rem 0 !important; }
.act-label { display: inline-flex !important; align-items: center; gap: .4rem;
  background: var(--md-primary-container) !important; color: var(--md-on-primary-container) !important;
  border-radius: var(--md-shape-s); padding: .3rem .75rem !important; margin-bottom: 1rem !important;
  font-size: .72rem !important; letter-spacing: .12em !important; font-weight: 600 !important; }
.act-title { font-family: var(--md-display) !important; font-size: 1.6rem !important; font-weight: 500 !important;
  color: var(--md-on-surface) !important; margin-bottom: .9rem !important; }
.act-body, .act-body p { color: var(--md-on-surface-variant) !important; font-size: 1.02rem !important;
  line-height: 1.75 !important; }
.act-body strong { color: var(--md-on-surface) !important; }
.act blockquote { border-left: 3px solid var(--md-primary) !important; color: var(--md-on-surface) !important;
  font-family: var(--md-display) !important; font-size: 1.3rem !important; }
/* warna inline lama di tabel akronim → token M3 (kontras ≥ 4.5:1) */
span[style*="#0F766E"], span[style*="rgb(15, 118, 110)"] { color: var(--md-tertiary) !important; }
span[style*="#C2410C"], span[style*="rgb(194, 65, 12)"] { color: var(--md-primary) !important;
  font-family: var(--md-display) !important; }
span[style*="#A8A29E"], span[style*="rgb(168, 162, 158)"] { color: var(--md-on-surface-variant) !important; }
.quote { min-height: 104px; background: var(--md-tertiary-container) !important; color: var(--md-on-tertiary-container) !important;
  border: none !important; border-radius: var(--md-shape-l) var(--md-shape-l) var(--md-shape-l) 4px !important;
  padding: 1.1rem 1.25rem !important; font-family: var(--md-display) !important; font-size: 1.05rem;
  box-shadow: var(--md-elev-1); }
.epilog { background: var(--md-surface-container) !important; border-radius: var(--md-shape-xl) !important;
  padding: 2.5rem !important; }
.epilog-list li { color: var(--md-on-surface-variant) !important; }
.epilog-list li::before { color: var(--md-primary) !important; }
.closing-quote { font-family: var(--md-display) !important; font-size: 1.5rem !important;
  color: var(--md-on-surface) !important; }
.pitch-card { background: var(--md-surface-container-low) !important;
  border: 1px solid var(--md-outline-variant) !important; border-left: 1px solid var(--md-outline-variant) !important;
  border-radius: var(--md-shape-l) !important; }
.pitch-label { display: inline-block; background: var(--md-secondary-container); color: var(--md-on-secondary-container) !important;
  border-radius: var(--md-shape-s); padding: .25rem .7rem; }
.pitch-body { color: var(--md-on-surface-variant) !important; }
.tagline-pill { background: transparent !important; border: 1px solid var(--md-outline) !important;
  border-radius: var(--md-shape-s) !important; color: var(--md-on-surface) !important;
  padding: .45rem .9rem !important; }

/* ── dashboard: badge → chip ── */
.badge { border-radius: var(--md-shape-s) !important; padding: .3rem .75rem !important;
  font-size: .78rem !important; font-weight: 600 !important; border: none !important; }
.badge-graf  { background: var(--md-primary-container) !important; color: var(--md-on-primary-container) !important; }
.badge-hub   { background: var(--md-tertiary-container) !important; color: var(--md-on-tertiary-container) !important; }
.badge-aktor { background: #4A2D6B !important; color: #EBDCFF !important; }
.badge-isi   { background: var(--md-secondary-container) !important; color: var(--md-on-secondary-container) !important; }
.badge-waktu { background: #003A75 !important; color: #D6E3FF !important; }

/* ── gerak ── */
@keyframes m3-rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
.act, .stat-box, .epilog, .pitch-card, .quote { animation: m3-rise .6s var(--md-ease) both; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }

/* ── layar kecil ── */
@media (max-width: 640px) {
  [data-testid="stMainBlockContainer"] { padding: 2.5rem 1rem 3rem; }
  .act, .epilog { padding: 1.4rem !important; border-radius: 20px !important; }
  .stat-val { font-size: 1.75rem !important; }
}
</style>
""".replace("__FONTS__", FONTS).replace("__VARS__", _vars())


def apply_m3() -> None:
    """Suntik tema M3. st.html berisi <style> saja tidak memakan ruang di halaman."""
    if hasattr(st, "html"):
        st.html(CSS)
    else:  # Streamlit lama
        st.markdown(CSS, unsafe_allow_html=True)
