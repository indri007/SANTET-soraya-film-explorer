"""
SANTET – Streamlit SNA Dashboard
Menampilkan semua 20 analisis jaringan (SNA) secara lengkap:
  - Grafik PNG + tabel CSV untuk setiap langkah
  - Navigasi sidebar per kategori
  - Filter set data
  - Unduh files
Jalankan: streamlit run streamlit_app/app.py
"""

import os, glob, re, textwrap
import streamlit as st
import pandas as pd

# ── path dasar ─────────────────────────────────────────────────────────────
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS = os.path.join(BASE, "results")

# ── metadata 20 perintah ───────────────────────────────────────────────────
COMMANDS = [
    (1,  "peta",              "Peta jaringan keseluruhan",            "🗺️ Gambar Graf"),
    (2,  "grup-kotak",        "Group-in-a-Box: komunitas",             "🗺️ Gambar Graf"),
    (3,  "per-film",          "Graf balasan per film (small multiples)","🗺️ Gambar Graf"),
    (4,  "warna-niat",        "Graf warna kategori komentar",          "🗺️ Gambar Graf"),
    (5,  "film-film",         "Proyeksi film–film",                   "🗺️ Gambar Graf"),
    (6,  "densitas",          "Densitas & komponen terhubung",         "🔗 Hubungan"),
    (7,  "komunitas",         "Komunitas Louvain + modularitas Q",     "🔗 Hubungan"),
    (8,  "irisan",            "Irisan penonton antar-film (Jaccard)",  "🔗 Hubungan"),
    (9,  "jembatan",          "Akun jembatan antar-komunitas",         "🔗 Hubungan"),
    (10, "rantai-balasan",    "Ukuran thread & % komentar dibalas",    "🔗 Hubungan"),
    (11, "resiprositas",      "Resiprositas balasan",                  "🔗 Hubungan"),
    (12, "aktor-aktif",       "Aktor paling aktif (out-degree)",       "🎭 Aktor"),
    (13, "aktor-direspons",   "Aktor paling direspons (in-degree)",    "🎭 Aktor"),
    (14, "perantara",         "Aktor perantara (betweenness)",         "🎭 Aktor"),
    (15, "aktor-inti",        "Aktor inti (PageRank)",                 "🎭 Aktor"),
    (16, "superfans",         "Superfans (≥3 film)",                  "🎭 Aktor"),
    (17, "kata-teratas",      "Kata teratas per film & komunitas",     "💬 Isi Komentar"),
    (18, "pasangan-kata",     "Pasangan kata (bigram)",               "💬 Isi Komentar"),
    (19, "emoji-tagar",       "Emoji & tagar teratas",                "💬 Isi Komentar"),
    (20, "waktu",             "Jaringan per jendela waktu",           "⏱️ Waktu"),
]

BY_NUM  = {n: (slug, title, kat) for n, slug, title, kat in COMMANDS}
CATS    = list(dict.fromkeys(kat for _, _, _, kat in COMMANDS))

# ── page config ────────────────────────────────────────────────────────────
try:
    st.set_page_config(
        page_title="SANTET · SNA Dashboard",
        page_icon="🕯️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    pass

# ── custom CSS (Material-3-inspired dark theme) ───────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .block-container { padding-top: 1.5rem; }
  h1 { font-size: 1.8rem; font-weight: 700; }
  h2 { font-size: 1.25rem; font-weight: 600; border-bottom: 2px solid #C2410C; padding-bottom: 4px; margin-top: 2rem; }
  h3 { font-size: 1.05rem; font-weight: 600; color: #C2410C; }
  .step-card {
    background: #1e1e2e; border-radius: 12px; padding: 1.2rem 1.4rem;
    margin-bottom: 2rem; border: 1px solid #2a2a3e;
  }
  .badge {
    display:inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; margin-right: 4px;
  }
  .badge-graf  { background:#C2410C22; color:#C2410C; border:1px solid #C2410C55; }
  .badge-hub   { background:#0F766E22; color:#0F766E; border:1px solid #0F766E55; }
  .badge-aktor { background:#7C3AED22; color:#7C3AED; border:1px solid #7C3AED55; }
  .badge-isi   { background:#B4530922; color:#B45309; border:1px solid #B4530955; }
  .badge-waktu { background:#1D4ED822; color:#1D4ED8; border:1px solid #1D4ED855; }
  .stat-row { display: flex; gap: 1rem; flex-wrap: wrap; margin: 0.5rem 0 1rem; }
  .stat-box {
    background: #12121e; border-radius: 8px; padding: 0.6rem 1.2rem;
    border: 1px solid #2a2a3e; flex: 1; min-width: 120px;
  }
  .stat-val { font-size: 1.4rem; font-weight: 700; color: #C2410C; }
  .stat-lbl { font-size: 0.7rem; color: #aaa; margin-top: 2px; }
  div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🕯️ **SANTET**")
    st.caption("Sentiment Analysis for Nusantara Theatrical Expectation Tracking")
    st.divider()

    # pilih folder SNA
    sna_dirs = sorted(glob.glob(os.path.join(RESULTS, "sna_*")), reverse=True)
    if not sna_dirs:
        st.error("Tidak ada folder `sna_*` di `results/`.\nJalankan: `./bit sna all`")
        st.stop()

    folder_labels = {d: os.path.basename(d) for d in sna_dirs}
    target_default = "sna_20261006_2128"
    default_idx = 0
    for idx, d in enumerate(sna_dirs):
        if os.path.basename(d) == target_default:
            default_idx = idx
            break

    sel_folder = st.selectbox("📁 Pilih hasil SNA:", sna_dirs, index=default_idx,
                              format_func=lambda d: folder_labels[d])

    st.divider()
    st.markdown("### 📋 Navigasi Analisis")

    # checkbox filter kategori
    show_cats = {}
    for cat in CATS:
        show_cats[cat] = st.checkbox(cat, value=True, key=f"cat_{cat}")

    st.divider()
    # tombol langsung ke analisis
    st.markdown("### 🔢 Loncat ke analisis")
    cols = st.columns(4)
    for i, (n, slug, title, kat) in enumerate(COMMANDS):
        with cols[i % 4]:
            st.markdown(f"[{n:02d}](#{slug})", unsafe_allow_html=False)

# ── header utama ───────────────────────────────────────────────────────────
st.markdown("# 🕸️ SANTET — Analisis Jaringan Komentar YouTube")

# baca ringkasan.md untuk stats header
md_path = os.path.join(sel_folder, "ringkasan.md")
stats_line = ""
if os.path.exists(md_path):
    with open(md_path, encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines[:5]:
        if "komentar" in line and "akun" in line:
            stats_line = line.strip().strip("_")
            break

if stats_line:
    # parse numbers
    nums = re.findall(r"[\d,]+", stats_line.replace(".", ","))
    parts = re.split(r"·", stats_line)
    cols = st.columns(len(parts))
    icons = ["📅", "💬", "👥", "🎬", "📦"]
    for i, part in enumerate(parts):
        with cols[i]:
            part = part.strip()
            st.markdown(f"""
            <div class="stat-box">
              <div class="stat-val">{icons[i] if i < len(icons) else "📊"}</div>
              <div class="stat-lbl">{part}</div>
            </div>""", unsafe_allow_html=True)

st.markdown(f"**Folder:** `{os.path.basename(sel_folder)}`")
st.divider()

# ── helper functions ───────────────────────────────────────────────────────
BADGE_CSS = {
    "🗺️ Gambar Graf":  "graf",
    "🔗 Hubungan":      "hub",
    "🎭 Aktor":         "aktor",
    "💬 Isi Komentar":  "isi",
    "⏱️ Waktu":         "waktu",
}

def render_step(n, slug, title, kat):
    """Render satu langkah analisis: PNG + semua CSV terkait."""
    badge_cls = BADGE_CSS.get(kat, "graf")
    st.markdown(f"""<div id="{slug}"></div>""", unsafe_allow_html=True)
    st.markdown(f"## {n:02d}. {title}")
    st.markdown(f'<span class="badge badge-{badge_cls}">{kat}</span>', unsafe_allow_html=True)

    folder = sel_folder
    # PNG
    png = os.path.join(folder, f"{n:02d}_{slug}.png")
    if os.path.isfile(png):
        try:
            st.image(png, width="stretch")
        except TypeError:
            st.image(png, use_container_width=True)
    else:
        st.info(f"Tidak ada grafik PNG untuk analisis {n:02d}.")

    # CSV(s) — mungkin ada lebih dari satu (misal 18_pasangan-kata*.csv)
    csvs = sorted(glob.glob(os.path.join(folder, f"{n:02d}_*.csv")))
    if csvs:
        tabs = st.tabs([os.path.basename(c) for c in csvs])
        for tab, csv_path in zip(tabs, csvs):
            with tab:
                try:
                    df = pd.read_csv(csv_path)
                    st.dataframe(df, width="stretch", height=min(400, 40 + 35 * len(df)))
                    with open(csv_path, "rb") as f:
                        st.download_button(
                            f"⬇️ Unduh {os.path.basename(csv_path)}",
                            f.read(),
                            file_name=os.path.basename(csv_path),
                            mime="text/csv",
                            key=f"dl_{n}_{os.path.basename(csv_path)}",
                        )
                except Exception as e:
                    st.warning(f"Gagal membaca CSV: {e}")
    elif not os.path.isfile(png):
        st.warning(f"Tidak ada file output untuk analisis {n:02d} di folder ini.")

    # penjelasan dari ringkasan.md (ekstrak seksi relevan)
    if os.path.exists(md_path):
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
        # Cari seksi yang cocok (## NN. Judul)
        pat = rf"## {n:02d}\. .+?\n(.*?)(?=\n## \d\d\.|\Z)"
        m = re.search(pat, content, re.S)
        if m:
            snippet = m.group(1).strip()
            # Hapus baris tabel panjang (sudah tampil sebagai dataframe)
            clean = "\n".join(
                l for l in snippet.splitlines()
                if not l.startswith("|") and not l.startswith(":-")
            ).strip()
            if clean:
                with st.expander("📝 Catatan ringkasan", expanded=False):
                    st.markdown(clean)

    # GraphML download jika ada
    graphml = os.path.join(folder, f"{n:02d}_{slug}.graphml")
    if os.path.isfile(graphml):
        with open(graphml, "rb") as f:
            st.download_button(
                "⬇️ Unduh GraphML (NodeXL/Gephi)",
                f.read(),
                file_name=os.path.basename(graphml),
                mime="application/xml",
                key=f"dl_gml_{n}",
            )

    st.divider()


# ── tampilkan semua analisis per kategori ──────────────────────────────────
current_cat = None
for n, slug, title, kat in COMMANDS:
    if not show_cats.get(kat, True):
        continue
    if kat != current_cat:
        current_cat = kat
        st.markdown(f"# {kat}")
    render_step(n, slug, title, kat)


# ── NodeXL export section ──────────────────────────────────────────────────
nodexl_dir = os.path.join(sel_folder, "nodexl")
edges_f  = os.path.join(nodexl_dir, "edges.csv")
verts_f  = os.path.join(nodexl_dir, "vertices.csv")
if os.path.isdir(nodexl_dir):
    st.markdown("# 📤 Ekspor NodeXL Pro")
    st.markdown("File di bawah ini siap diimpor ke **NodeXL Pro** (Import → From Open Workbook).")
    c1, c2 = st.columns(2)
    if os.path.isfile(edges_f):
        df_e = pd.read_csv(edges_f)
        with c1:
            st.markdown(f"**edges.csv** ({len(df_e):,} sisi)")
            st.dataframe(df_e.head(50), width="stretch")
            with open(edges_f, "rb") as f:
                st.download_button("⬇️ Unduh edges.csv", f.read(),
                                   file_name="edges.csv", mime="text/csv", key="dl_edges")
    if os.path.isfile(verts_f):
        df_v = pd.read_csv(verts_f)
        with c2:
            st.markdown(f"**vertices.csv** ({len(df_v):,} simpul)")
            st.dataframe(df_v.head(50), width="stretch")
            with open(verts_f, "rb") as f:
                st.download_button("⬇️ Unduh vertices.csv", f.read(),
                                   file_name="vertices.csv", mime="text/csv", key="dl_verts")

# ── footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🕯️ **SANTET** · Sentiment Analysis for Nusantara Theatrical Expectation Tracking  \n"
    "Riset independen — tidak berafiliasi dengan Soraya Intercine Films, Hitmaker Studios, atau MD Pictures.  \n"
    "GitHub: [indri007/soraya-film-explorer](https://github.com/indri007/soraya-film-explorer)"
)
