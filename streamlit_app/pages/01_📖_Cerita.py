"""
pages/01_📖_Cerita.py
Halaman narasi SANTET: Prolog → Epilog + versi siap pakai.
Ditampilkan sebagai halaman pertama di sidebar Streamlit multi-page.
"""
import streamlit as st

st.set_page_config(
    page_title="SANTET · Cerita",
    page_icon="🕯️",
    layout="wide",
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,600;0,700;1,400&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
  text-align: center;
  padding: 3.5rem 1rem 2rem;
  background: linear-gradient(160deg, #0a0a14 0%, #1a0c04 100%);
  border-radius: 16px;
  margin-bottom: 2rem;
}
.hero-title {
  font-size: 3rem; font-weight: 700; letter-spacing: -1px;
  background: linear-gradient(90deg, #C2410C, #F97316, #C2410C);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin: 0; line-height: 1.1;
}
.hero-sub {
  font-size: 1rem; color: #A8A29E; margin: 0.5rem 0 0;
  letter-spacing: 0.12em; text-transform: uppercase;
}
.hero-tagline {
  font-size: 1.25rem; color: #E7E5E4; font-style: italic;
  margin: 1.5rem 0 0.25rem;
}
.act {
  background: #12121e; border-left: 3px solid #C2410C;
  border-radius: 0 12px 12px 0; padding: 1.4rem 1.8rem;
  margin: 1.5rem 0;
}
.act-label {
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.15em;
  text-transform: uppercase; color: #C2410C; margin-bottom: 0.4rem;
}
.act-title { font-size: 1.2rem; font-weight: 700; color: #E7E5E4; margin: 0 0 1rem; }
.act-body  { color: #D6D3D1; line-height: 1.8; font-size: 0.97rem; }
.quote {
  border-left: 3px solid #0F766E; padding: 0.8rem 1.4rem;
  background: #0d1f1e; border-radius: 0 8px 8px 0;
  color: #99F6E4; font-style: italic; margin: 1rem 0;
}
.akronim-row {
  display: grid; grid-template-columns: 3rem 7rem 1fr 2fr;
  gap: 0.5rem 1.2rem; align-items: start;
  border-bottom: 1px solid #2a2a3e; padding: 0.55rem 0;
}
.akronim-letter { font-size: 1.3rem; font-weight: 700; color: #C2410C; }
.akronim-kata   { font-weight: 600; color: #E7E5E4; }
.akronim-makna  { color: #0F766E; font-weight: 600; }
.akronim-janji  { color: #A8A29E; font-size: 0.88rem; }
.epilog {
  background: #12121e; border-radius: 12px; padding: 2rem 2.4rem;
  text-align: center; margin: 2rem 0;
}
.epilog-list { list-style: none; padding: 0; margin: 1rem 0; }
.epilog-list li { color: #D6D3D1; padding: 0.3rem 0; font-size: 0.97rem; }
.epilog-list li::before { content: "▸ "; color: #C2410C; }
.closing-quote {
  font-size: 1.1rem; color: #E7E5E4; font-style: italic;
  line-height: 1.7; margin-top: 1.5rem;
}
.pitch-card {
  background: #1e1e2e; border: 1px solid #2a2a3e; border-radius: 12px;
  padding: 1.4rem 1.8rem; margin: 1.2rem 0;
}
.pitch-label {
  font-size: 0.72rem; font-weight: 600; letter-spacing: 0.15em;
  text-transform: uppercase; color: #7C3AED; margin-bottom: 0.8rem;
}
.pitch-body { color: #D6D3D1; line-height: 1.8; font-size: 0.95rem; }
.tagline-pill {
  display: inline-block; background: #1a0c04; border: 1px solid #C2410C44;
  border-radius: 20px; padding: 0.35rem 1rem; margin: 0.3rem;
  color: #F97316; font-size: 0.88rem; font-style: italic;
}
.stat-trio { display: flex; gap: 1rem; margin: 1.2rem 0; flex-wrap: wrap; }
.stat-box {
  background: #0a0a14; border: 1px solid #2a2a3e; border-radius: 10px;
  padding: 0.8rem 1.2rem; flex: 1; min-width: 140px; text-align: center;
}
.stat-val { font-size: 1.5rem; font-weight: 700; color: #C2410C; }
.stat-lbl { font-size: 0.72rem; color: #A8A29E; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)


# ── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-sub">Sentiment Analysis for Nusantara Theatrical Expectation Tracking</p>
  <h1 class="hero-title">SANTET</h1>
  <p class="hero-tagline">"Membaca 'mantra' warganet sebelum film tayang."</p>
  <p style="color:#6B7280;font-size:0.8rem;margin-top:1rem;">
    Riset independen · tidak berafiliasi dengan Soraya Intercine Films, Hitmaker Studios, atau MD Pictures
  </p>
</div>
""", unsafe_allow_html=True)

# ── STATS KILAT ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="stat-trio">
  <div class="stat-box"><div class="stat-val">9.840</div><div class="stat-lbl">komentar trailer dikumpulkan</div></div>
  <div class="stat-box"><div class="stat-val">15</div><div class="stat-lbl">film terverifikasi (2017–2026)</div></div>
  <div class="stat-box"><div class="stat-val">51,2%</div><div class="stat-lbl">komentar horor dibaca "negatif" oleh model standar</div></div>
  <div class="stat-box"><div class="stat-val">10,0%</div><div class="stat-lbl">negatif sesungguhnya (leksikon horor)</div></div>
</div>
<p style="color:#6B7280;font-size:0.75rem;margin-bottom:2rem;">
  Angka dari <code>data/films_clean.csv</code> dan <code>results/sna_*/ringkasan.md</code>.
  Sentimen IndoBERT belum tervalidasi secara manual.
</p>
""", unsafe_allow_html=True)

st.divider()

# ── PROLOG ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="act">
  <div class="act-label">Prolog</div>
  <div class="act-title">Malam sebelum tayang</div>
  <div class="act-body">
    <p>Jam dua belas malam, beberapa hari sebelum film perdana. Di sebuah kantor produksi di Jakarta,
    lampu masih menyala. Poster sudah tercetak dan jadwal tayang sudah dikunci. Tahun-tahun kerja,
    ratusan kru, dan mimpi seorang sutradara kini menunggu satu jawaban: <strong>apakah penonton akan datang?</strong></p>
    <p>Jawabannya sebenarnya sudah ditulis ribuan kali, malam itu juga, di kolom komentar trailer:</p>
  </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="quote">"Serem banget anjir, merinding parah."</div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="quote">"Gas nonton hari pertama!"</div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="quote">"Ga berani nonton sendirian, ajak bestie 😭🔥"</div>
    """, unsafe_allow_html=True)

st.markdown("""
<p style="color:#A8A29E;font-size:0.92rem;padding:0 0.5rem;">
  Itulah mantranya. Bukan kutukan, tapi doa dari penonton yang sudah tidak sabar.
  Masalahnya, belum ada yang bisa membacanya.
</p>
""", unsafe_allow_html=True)

# ── BABAK I ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="act">
  <div class="act-label">Babak I</div>
  <div class="act-title">Kutukan yang sebenarnya</div>
  <div class="act-body">
    <p>Industri film Indonesia hidup dari rasa takut. Horor adalah genre yang paling sering mengisi
    layar bioskop dan paling sering mencetak jutaan penonton. Tetapi industri ini bekerja dalam gelap.</p>
    <p>Di studio yang sama, dengan genre dan mesin promosi yang sama, satu film ditonton
    <strong>3.346.216</strong> orang (<em>Suzzanna: Bernapas dalam Kubur</em>, 2018), sementara
    film lain hanya <strong>525.034</strong> orang (<em>Racun Sangga</em>, 2024, angka berjalan).
    Selisihnya enam kali lipat, dan baru ketahuan setelah semuanya terlambat.</p>
    <p>Inilah kutukan sebenarnya: <strong>ketidakpastian</strong>. Film yang bagus bisa hilang dari
    layar dalam seminggu, dan karya yang digarap dengan sungguh-sungguh bisa tidak menemukan
    penontonnya. Bukan karena tidak ada yang mau menonton, tetapi karena tidak ada yang mendengar
    ketika mereka sudah berteriak ingin datang.</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── BABAK II ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="act">
  <div class="act-label">Babak II</div>
  <div class="act-title">Mesin yang tuli</div>
  <div class="act-body">
    <p>Kita sudah punya kecerdasan buatan yang bisa membaca jutaan kalimat dalam hitungan detik.
    Tapi ketika diminta membaca penonton horor Indonesia, ia gagal.</p>
    <p>Dari <strong>9.840 komentar trailer</strong> yang kami kumpulkan, model sentimen standar
    menyimpulkan bahwa lebih dari separuhnya (<strong>51,2%</strong>) negatif. Leksikon yang
    memahami horor hanya menemukan <strong>10,0%</strong>.</p>
    <p>Mesin itu mendengar <em>"takut"</em> dan menyimpulkan <em>"benci"</em>. Ia mendengar
    <em>"merinding"</em> dan mengira penonton kecewa. Teknologi yang dibangun dengan bahasa dan
    selera bangsa lain dipaksa membaca rasa bangsa ini — dan hasilnya suara jutaan penonton
    Nusantara salah dibaca.</p>
    <p style="font-size:0.8rem;color:#6B7280;">
      Catatan: angka sentimen IndoBERT 51,2% adalah output model belum tervalidasi manual.
      Lihat <code>results/paper_status.md</code> untuk status validasi terkini.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── BABAK III ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="act">
  <div class="act-label">Babak III</div>
  <div class="act-title">Bangsa yang tak tercatat</div>
  <div class="act-body">
    <p>Di jurnal-jurnal ilmiah dunia, prediksi box office sudah menjadi cabang ilmu yang mapan.
    Ada Hollywood, China, Korea, dan India. Indonesia, dengan sejarah horor sejak era Suzzanna,
    dengan bioskop yang penuh setiap musim Lebaran, dan dengan penonton yang setia membeli tiket
    untuk merasa takut bersama, hampir tidak tercatat.</p>
    <p><em>Seolah-olah selera kita tidak cukup penting untuk dipelajari.</em></p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── BABAK IV ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="act" style="border-left-color:#7C3AED;">
  <div class="act-label" style="color:#7C3AED;">Babak IV</div>
  <div class="act-title">Lahirnya SANTET</div>
  <div class="act-body">
    <p>SANTET lahir dari satu keyakinan sederhana:</p>
    <blockquote style="font-size:1.1rem;font-weight:600;color:#E7E5E4;
      border-left:3px solid #7C3AED;padding-left:1rem;margin:1rem 0;">
      Penonton Indonesia sudah berbicara. Kita hanya perlu belajar mendengar.
    </blockquote>
    <p>Setiap huruf dalam namanya adalah janji:</p>
  </div>
</div>
""", unsafe_allow_html=True)

# Tabel akronim
AKRONIM = [
    ("S", "Sentiment",  "Rasa",       "Tidak ada lagi rasa takut yang dibaca sebagai benci"),
    ("A", "Analysis",   "Ketelitian", "Jujur pada data, termasuk ketika hasilnya belum sesuai harapan"),
    ("N", "Nusantara",  "Akar",       "Dibangun dari bahasa, slang, emoji, dan budaya kita sendiri"),
    ("T", "Theatrical", "Layar",      "Agar karya lokal tetap bertahan di bioskop"),
    ("E", "Expectation","Harapan",    "Mengukur niat menonton, bukan sekadar kesan"),
    ("T", "Tracking",   "Waktu",      "Membaca sebelum tayang, saat keputusan masih bisa diubah"),
]

cols = st.columns([1, 3, 2, 4])
cols[0].markdown("**Huruf**")
cols[1].markdown("**Makna**")
cols[2].markdown("**Nilai**")
cols[3].markdown("**Janji**")
st.divider()
for letter, word, value, promise in AKRONIM:
    c0, c1, c2, c3 = st.columns([1, 3, 2, 4])
    c0.markdown(f"<span style='font-size:1.5rem;font-weight:700;color:#C2410C;'>{letter}</span>",
                unsafe_allow_html=True)
    c1.markdown(f"**{word}**")
    c2.markdown(f"<span style='color:#0F766E;font-weight:600;'>{value}</span>", unsafe_allow_html=True)
    c3.markdown(f"<span style='color:#A8A29E;font-size:0.88rem;'>{promise}</span>", unsafe_allow_html=True)

st.markdown("""
<p style="color:#D6D3D1;line-height:1.8;margin-top:1.5rem;padding:0 0.5rem;">
  Kalau santet dalam cerita rakyat adalah kekuatan tak terlihat yang bekerja dari jauh,
  <strong>SANTET ini adalah kebalikannya: kekuatan tak terlihat yang akhirnya dibuat terlihat.</strong>
  Bukan untuk mencelakai, tetapi untuk menyelamatkan karya.
</p>
""", unsafe_allow_html=True)

# ── EPILOG ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="epilog">
  <div class="act-label" style="text-align:center;margin-bottom:1rem;">Epilog</div>
  <p style="font-size:1.1rem;font-weight:600;color:#E7E5E4;">Untuk siapa SANTET dibuat</p>
  <ul class="epilog-list">
    <li>Untuk <strong>produser</strong> yang tidak ingin lagi bertaruh dalam gelap.</li>
    <li>Untuk <strong>sineas</strong> agar karyanya punya kesempatan menemukan penonton.</li>
    <li>Untuk <strong>penonton</strong> yang suaranya selama ini disalahartikan.</li>
    <li>Untuk <strong>ilmu pengetahuan</strong>, agar Nusantara punya tempat di peta riset dunia.</li>
  </ul>
  <div class="closing-quote">
    "Mereka menjerit karena ingin datang.<br>
    SANTET hadir agar jeritan itu akhirnya didengar."
  </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── VERSI SIAP PAKAI ────────────────────────────────────────────────────────
st.markdown("## 🎙️ Versi Siap Pakai")

st.markdown("""
<div class="pitch-card">
  <div class="pitch-label">Elevator Pitch · 30 detik</div>
  <div class="pitch-body">
    Setiap film horor Indonesia adalah taruhan besar, dan industrinya masih menebak dalam gelap.
    Padahal penonton sudah memberi tanda di kolom komentar trailer. Masalahnya, AI membaca
    <em>"serem banget"</em> sebagai keluhan, padahal itu pujian. SANTET adalah sistem analisis
    sentimen yang dirancang untuk bahasa penonton horor Nusantara — membaca niat menonton
    sebelum film tayang, secara etis dan terbuka.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("**Tagline alternatif:**")
st.markdown("""
<div style="margin: 0.5rem 0 1.5rem;">
  <span class="tagline-pill">"Membaca 'mantra' warganet sebelum film tayang."</span>
  <span class="tagline-pill">"Rasa takut adalah permintaan."</span>
  <span class="tagline-pill">"Karena 'merinding' bukan keluhan."</span>
  <span class="tagline-pill">"Suara penonton Nusantara, akhirnya terbaca."</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="pitch-card" style="border-left:3px solid #0F766E;">
  <div class="pitch-label" style="color:#0F766E;">Pembuka Presentasi · Slide 1</div>
  <div class="pitch-body" style="font-style:italic;font-size:1.05rem;line-height:1.9;">
    "Bayangkan Anda sudah bekerja tiga tahun untuk satu film. Malam sebelum tayang,
    ribuan orang menulis bahwa mereka ketakutan. Dan mesin terpintar di dunia memberi
    tahu Anda: mereka membencinya. Kami membangun SANTET karena kami tahu itu tidak benar."
  </div>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ──────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "🕯️ **SANTET** · Riset akademik independen · MIT License  \n"
    "Tidak berafiliasi dengan Soraya Intercine Films, Hitmaker Studios, atau MD Pictures.  \n"
    "GitHub: [indri007/prediksi-movie-2027](https://github.com/indri007/prediksi-movie-2027)"
)
