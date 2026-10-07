# 🕯️ SANTET
### Sentiment Analysis for Nusantara Theatrical Expectation Tracking

<div align="center">

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://santet-soraya-film-explorer.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-indri007%2Fprediksi--movie--2027-181717?logo=github)](https://github.com/indri007/prediksi-movie-2027)
[![Interactive 3D](https://img.shields.io/badge/Interactive%203D-GitHub%20Pages-blueviolet?logo=three.js)](https://indri007.github.io/prediksi-movie-2027/docs/santet/)
[![Status](https://img.shields.io/badge/Status-Riset%20Berjalan-orange)](results/paper_status.md)
[![Lisensi](https://img.shields.io/badge/Lisensi-MIT-green)](LICENSE)
[![UU PDP](https://img.shields.io/badge/Kepatuhan-UU%20PDP%20No.%2027%2F2022-blue)](docs/DESIGN.md#etika)

<br/>

### 🔗 Tautan Publik & Demo Interaktif
| Layanan | Tautan | Keterangan |
|---|---|---|
| 🕯️ **Streamlit Cloud App** | [santet-soraya-film-explorer.streamlit.app](https://santet-soraya-film-explorer.streamlit.app) | Live App: Cerita SANTET & 20 Analisis SNA |
| 🌐 **Narasi 3D Interaktif** | [indri007.github.io/.../docs/santet/](https://indri007.github.io/prediksi-movie-2027/docs/santet/) | Pengalaman cerita 3D Six-Act berbasis Three.js |
| 🐙 **Repositori GitHub** | [indri007/prediksi-movie-2027](https://github.com/indri007/prediksi-movie-2027) | Kode sumber, dataset terverifikasi, & pipeline |
| 🕸️ **Hasil SNA Pilihan** | [results/sna_20261006_2128/](results/sna_20261006_2128/) | 5.666 simpul · 7.431 sisi · 13 film |

<br/>

<a href="https://santet-soraya-film-explorer.streamlit.app">
  <img src="docs/assets/santet_hero.svg" width="100%" alt="Animasi SANTET 6 babak — ilustratif: Prolog, Kutukan, Mesin yang tuli, Bangsa tak tercatat, Lahirnya SANTET, Epilog. Label: ilustratif.">
</a>

*Animasi di atas bersifat ilustratif. Klik untuk membuka live app Streamlit / narasi interaktif.*

**"Membaca 'mantra' warganet sebelum film tayang."**  
*Fear is demand · Rasa takut adalah permintaan*

</div>

---

## Kenapa SANTET ada

Film horor Indonesia dari studio yang sama bisa berbeda perolehan penonton hingga enam kali lipat — namun selisih itu baru terlihat setelah film tutup layar. Komentar trailer di YouTube sudah memuatnya lebih awal: kata *"serem banget"* dan *"gas nonton"* adalah sinyal niat menonton, bukan keluhan, tetapi model sentimen standar membacanya sebagai negatif. SANTET membangun pipeline analisis sentimen, jaringan komentar, dan korelasi YouTube–box office yang sadar konteks budaya Nusantara, dengan standar reproduktifitas dan etika data yang ketat. Tujuannya bukan hanya riset — melainkan agar keputusan praproduksi dan distribusi bisa bersandar pada sinyal yang lebih jujur.

---

## Status Riset (per 06-10-2026)

> Angka-angka ini adalah hasil aktual. Tidak ada angka yang dibulatkan atau dipercantik.

| Komponen | Status | Keterangan |
|---|:---:|---|
| Dataset box office terverifikasi (15 film, URL resmi) | ✅ | `data/films_clean.csv` |
| Scrape komentar YouTube (9.840 komentar, 4 set) | ✅ | `yt_soraya/`, `yt_md/`, `yt_hitmaker/`, `yt_ivanna/` |
| Korelasi Spearman: `likes_total` vs penonton | ✅ | ρ = 0,571 · p = 0,026 · CI 95% [0,05 – 0,86] |
| Koreksi multi-testing Benjamini–Hochberg | ⚠️ | q = 0,26 — tidak lolos koreksi BH; butuh n lebih besar |
| Sentimen IndoBERT (belum tervalidasi manual) | ⚠️ | 0 dari ≥30 label manusia terkumpul |
| Model prediktif LOOCV (n = 14) | ⚠️ | MAPE 85,8% vs baseline 70,3% — model belum mengungguli baseline |
| Anotasi Google Trends pra-rilis | ⏳ | `trends_pra_rilis` tersedia untuk 13/15 film |
| Komentar YouTube API (tanggal presisi) | ⏳ | Butuh `YT_API_KEY` |
| Validasi sentimen oleh manusia (≥30 baris) | ⏳ | Lembar anotasi siap di `annotation/` |
| 20 analisis SNA Louvain | ✅ | `results/sna_*/` · Q = 0,810 (13 komunitas) |

---

## Quick Start

```bash
# 1. Pasang dependensi
pip install -r requirements-pipeline.txt   # atau: ./bit install  (requirements.txt = dependensi ringan Streamlit Cloud)

# 2. Unduh komentar trailer (yt-dlp, tanpa API key)
./bit scrape all --max 500

# 3. Jalankan semua analisis: sentimen → SNA → korelasi
./bit finish
```

Butuh data pra-rilis presisi? `export YT_API_KEY="..." && ./bit precise all`

---

## Peta Fitur

| Modul | Perintah | Output |
|---|---|---|
| **CLI terpadu** | `./bit help` | Semua 30+ perintah dalam satu entrypoint |
| **Scrape trailer** | `./bit scrape [soraya|md|hitmaker|all]` | `yt_*/comments.csv`, `videos.csv`, `edges.csv` |
| **Sentimen IndoBERT** | `./bit sentiment predict` | Label + skor per komentar |
| **20 analisis SNA** | `./bit sna all` | Graf, tabel, `ringkasan.md`, NodeXL export |
| **Korelasi & model** | `./bit correlate` · `./bit model` | Spearman, bootstrap, LOOCV, BH |
| **Dashboard web** | `./bit dashboard` | `dashboard/index.html` (dark glassmorphism) |
| **Streamlit SNA & Cerita** | [santet-soraya-film-explorer.streamlit.app](https://santet-soraya-film-explorer.streamlit.app) | Cerita SANTET & 20 grafik SNA interaktif |
| **Narasi 3D** | [docs/santet/](https://indri007.github.io/prediksi-movie-2027/docs/santet/) | Six-act story · Material 3 · Three.js |

---

## Data & Etika

**Independensi.** SANTET adalah riset akademik independen. Tidak berafiliasi dengan, didukung oleh, atau disponsori oleh Soraya Intercine Films, Hitmaker Studios, atau MD Pictures. Judul film, metadata trailer, dan angka penonton dikutip semata untuk tujuan ilmiah dan pendidikan.

**Privasi (UU PDP No. 27/2022).** Seluruh identitas komentator dipseudonimkan dengan HMAC-SHA256 + salt rahasia (`SORAYA_SALT`). Teks komentar mentah dan ID unik YouTube tidak disebarkan ke repositori publik.

**Angka sementara.** Penonton *Racun Sangga* (525.034) dan *Suzzanna: Santet Dosa di Atas Dosa* (1.054.864) adalah angka berjalan per laporan publik terakhir yang dikutip; bukan angka final.

**Klaim yang tidak kami buat:**  
Kami tidak mengklaim "pertama", "akurat", atau "Scopus Q1 Ready". Model prediktif saat ini tidak lebih baik dari baseline rata-rata (MAPE 85,8% vs 70,3%). Sentimen IndoBERT belum tervalidasi secara manual.

---

## Dataset (15 Film, 2017–2026)

Sumber: `data/films_clean.csv` · Verifikasi: `AUDIT_REPORT.md`

| Judul | Studio | Tahun | Penonton | Status |
|---|---|:---:|---:|:---:|
| Ipar Adalah Maut | MD Pictures | 2024 | 4.775.315 | Final |
| Badarawuhi di Desa Penari | MD Pictures | 2024 | 4.013.558 | Final |
| Suzzanna: Bernapas dalam Kubur | Soraya Intercine Films | 2018 | 3.346.216 | Final |
| Ivanna | MD Pictures | 2022 | 2.793.775 | Final |
| Suzzanna: Malam Jumat Kliwon | Soraya Intercine Films | 2023 | 2.189.363 | Final |
| The Doll 3 | Hitmaker Studios | 2022 | 1.764.077 | Final |
| Sabrina | Hitmaker Studios | 2018 | 1.337.510 | Final |
| Mata Batin | Hitmaker Studios | 2017 | 1.282.557 | Final |
| Suzzanna: Santet Dosa di Atas Dosa | Soraya Intercine Films | 2026 | 1.054.864 | Berjalan* |
| Santet Segoro Pitu | Hitmaker Studios (ko-prod) | 2024 | 1.025.000 | Final |
| Indigo: What Do You See? | Hitmaker / Legacy Pictures | 2023 | 1.015.231 | Final |
| Jurnal Risa by Risa Saraswati | MD Pictures | 2024 | 865.045 | Final |
| Catatan Harian Menantu Sinting | Soraya Intercine Films | 2024 | 713.862 | Final |
| Perewangan | MD Pictures | 2024 | 658.000 | Final |
| Racun Sangga | Soraya Intercine Films | 2024 | 525.034 | Berjalan* |

*\*Angka berjalan per laporan publik; belum final.*

---

## Sitasi

```bibtex
@misc{sari2026santet,
  author = {Sari, Indri Anjar Kartika},
  title  = {The Scream Is a Compliment: Fear-as-Demand Signals and the
             Pre-Release Prediction of Indonesian Horror Box Office ---
             Evidence from Soraya Intercine Films},
  year   = {2026},
  note   = {Working paper},
  url    = {https://github.com/indri007/prediksi-movie-2027}
}
```

---

## Struktur Repositori

```
├── bit                        CLI terpadu (30+ perintah)
├── data/
│   ├── films_clean.csv        Master dataset terverifikasi (15 film)
│   └── box_office_sources.csv Log sumber angka penonton ber-URL
├── yt_soraya/ yt_md/ …        Komentar & metadata per set studio
├── results/
│   ├── sna_*/                 20 analisis SNA (PNG, CSV, GraphML)
│   ├── correlation_*/         Spearman, bootstrap, BH
│   └── model_*/               LOOCV MAPE
├── dashboard/                 Web dashboard dark glassmorphism
├── streamlit_app/app.py       Dashboard SNA interaktif (Streamlit)
├── docs/
│   ├── assets/santet_hero.svg Hero animasi SVG (ilustratif)
│   ├── santet/index.html      Narasi 3D interaktif (six-act)
│   └── DESIGN.md              Design system proyek
├── annotation/                Lembar anotasi manual (2 anotator)
├── AUDIT_REPORT.md            Audit metodologis & provenance data
├── requirements.txt            # dependensi Streamlit Cloud
└── requirements-pipeline.txt   # pipeline lengkap
```

---

<div align="center">
<sub>Riset independen · Tidak berafiliasi dengan studio manapun · MIT License</sub>
</div>
