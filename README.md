# 🎬 Soraya Film Explorer — Indonesian Box Office Prediction 2026/2027

<div align="center">

**Prediksi Penonton Bioskop Indonesia Berbasis Sinyal YouTube, Analisis Jaringan NodeXL, Sentimen IndoBERT & Google Trends**  
*Studi Komparatif: Soraya Intercine Films, Hitmaker Studios & MD Pictures (2017–2026)*

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch MPS](https://img.shields.io/badge/PyTorch-Apple%20Silicon%20MPS-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/NLP-IndoBERT%20%7C%20RoBERTa-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/w11wo/indonesian-roberta-base-sentiment-classifier)
[![NetworkX](https://img.shields.io/badge/SNA-NodeXL%20%7C%20NetworkX-blue)](https://networkx.org/)
[![Significance](https://img.shields.io/badge/Spearman%20%CF%81-0.571%20(p%3D0.026)-success)]()
[![Ethics](https://img.shields.io/badge/Compliance-UU%20PDP%20No.%2027%2F2022-brightgreen)]()
[![Status](https://img.shields.io/badge/Research-Scopus%20Q1%20Ready-purple)]()

---

*"Dari sinyal online pra-rilis trailer YouTube & Google Trends → estimasi akurat jumlah penonton bioskop Indonesia 2026/2027"*

</div>

---

## 📌 Ringkasan Proyek (Overview)

**Soraya Film Explorer** adalah pipeline data analitik dan platform pemodelan prediktif terpadu yang mengeksplorasi sinyal antusiasme publik di ranah digital (YouTube Video Engagement, NodeXL Video Co-commenting Networks, Analisis Sentimen IndoBERT + Emoji, dan Puncak Google Trends) untuk memproyeksikan perolehan jumlah penonton bioskop (*theatrical box office*) film Indonesia.

Berdasarkan Product Requirement Document (PRD oleh **@Indri**), riset ini meneliti film keluaran **Soraya Intercine Films** (salah satu rumah produksi tertua di Indonesia, berdiri 1982) dan afiliasinya **Hitmaker Studios**, serta diperluas dengan tolok ukur film blockbuster **MD Pictures** sebagai pembanding industri.

---

## 🎯 Pertanyaan Riset (Research Questions)

| # | Pertanyaan Riset | Temuan Utama & Status |
|---|---|---|
| **RQ1** | Seberapa kuat korelasi sinyal online (Views, Likes, Komentar) dengan total penonton bioskop? | **Terverifikasi:** `likes_total` adalah prediktor terkuat ($\rho = 0.571, p = 0.026 < 0.05$ signifikan eksak, $n = 15$). Audiens berkomitmen lewat 'Like' lebih berkorelasi dibanding penonton video pasif (`views_total`, $\rho = 0.286$). |
| **RQ2** | Berapa hari sebelum rilis sinyal online mulai memuncak (*lead time*)? | **Terverifikasi:** Minat Google Trends dan laju komentar trailer memuncak rata-rata **10,9 hari (~11 hari)** sebelum tanggal rilis resmi bioskop. |
| **RQ3** | Apakah sentimen komentar trailer menambah daya prediksi di atas volume numerik? | **Temuan Kritis:** Model NLP standar mengalami bias domain horor (kata *"serem"*, *"merinding"* salah dilabeli negatif). Koreksi leksikon emoji membuktikan polaritas negatif murni hanya 0–3,6%. Sentimen polaritas umum memiliki korelasi lemah ($\rho = 0.121$), menegaskan perlunya pengukuran *intensi menonton*. |
| **RQ4** | Faktor apa yang membedakan film laris vs kurang laris? | **Terverifikasi:** Kekuatan waralaba (*Franchise IP* seperti Suzzanna, KKN Universe) dan momen rilis liburan (Lebaran) memiliki korelasi parsial signifikan terhadap pencapaian box office di atas 1–4 juta penonton. |

---

## 📊 Matriks Dataset & Hasil Empiris ($n = 15$ Film)

Seluruh data penonton bersumber resmi dari [filmindonesia.or.id](https://filmindonesia.or.id), Cinepoint, rujukan ensiklopedia, dan laporan resmi produser:

| Judul Film | Rumah Produksi | Tahun | Penonton | Likes Trailer | Views Trailer | Komentar | Sentimen Positif | Sumber Resmi |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Ipar Adalah Maut** | MD Pictures | 2024 | 4.775.315 | 13.022 | 2.409.913 | 426 | 25,8% | filmindonesia.or.id |
| **Badarawuhi di Desa Penari** | MD Pictures | 2024 | 4.013.558 | 17.065 | 2.624.610 | 500 | 28,2% | filmindonesia.or.id |
| **Suzzanna: Bernapas dalam Kubur** | Soraya Intercine | 2018 | 3.346.216 | 52.629 | 9.647.484 | 500 | 36,0% | filmindonesia.or.id |
| **Ivanna** | MD Pictures | 2022 | 2.793.775 | 102.946 | 7.629.600 | 1.000 | 46,6% | filmindonesia.or.id |
| **Suzzanna: Malam Jumat Kliwon** | Soraya Intercine | 2023 | 2.189.363 | 29.542 | 4.869.567 | 1.728 | 45,7% | Wikipedia EN |
| **The Doll 3** | Hitmaker Studios | 2022 | 1.764.077 | 29.076 | 6.679.661 | 680 | 21,0% | Wikipedia EN |
| **Sabrina** | Hitmaker Studios | 2018 | 1.337.510 | 4.320 | 809.423 | - | - | filmindonesia.or.id |
| **Mata Batin** | Hitmaker Studios | 2017 | 1.282.557 | 2.877 | 542.865 | 105 | 17,1% | filmindonesia.or.id |
| **The Doll 2** | Hitmaker Studios | 2017 | 1.226.864 | 69.000 | 3.100.000 | - | - | filmindonesia.or.id |
| **Suzzanna: Santet Dosa di Atas Dosa** | Soraya Intercine | 2026 | 1.054.864* | 10.417 | 3.187.674 | 1.215 | 39,4% | Cinepoint / IDN Times |
| **Santet Segoro Pitu** | Hitmaker Studios | 2024 | 1.025.000 | 7.019 | 3.773.589 | 425 | 30,6% | IDN Times |
| **Indigo: What Do You See?** | Hitmaker / Legacy | 2023 | 1.015.231 | 12.378 | 3.147.375 | 793 | 43,1% | Wikipedia ID |
| **Jurnal Risa by Risa Saraswati** | MD Pictures | 2024 | 865.045 | 15.483 | 1.433.003 | 792 | 28,3% | filmindonesia.or.id |
| **Catatan Harian Menantu Sinting** | Soraya Intercine | 2024 | 713.862 | 17.909 | 2.151.656 | 257 | 18,7% | filmindonesia.or.id |
| **Perewangan** | MD Pictures | 2024 | 658.000 | 3.415 | 940.060 | 299 | 23,7% | Cinepoint |
| **Racun Sangga** | Soraya Intercine | 2024 | 525.034* | 2.393 | 5.359.442 | 198 | 40,4% | Pikiran Rakyat / IG |

*\*Angka sementara per laporan publik.*

---

## 🔬 Arsitektur Pipeline & Perintah CLI (`./bit`)

Manajemen seluruh ekosistem penelitian dijalankan melalui antarmuka baris perintah terpadu `./bit`:

```bash
# 1. Akuisisi Data Trailer & Komentar (yt-dlp, quota-free)
./bit check all               # Verifikasi integritas video ID trailer resmi
./bit scrape all              # Pengunduhan metadata dan komentar publik
./bit convert all             # Konversi menjadi videos.csv, comments.csv, edges.csv

# 2. Pemrosesan Bahasa Alami (NLP & IndoBERT)
./bit sentiment predict       # Klasifikasi sentimen transformer (w11wo/indonesian-roberta) + MPS Apple Silicon
./bit sentiment sample        # Pembuatan sampel anotasi manual (2 annotator sheet)
./bit sentiment validate      # Evaluasi reliabilitas (Cohen's Kappa & akurasi vs leksikon)
./bit sentiment finetune      # Fine-tuning spesifik domain horor Indonesia

# 3. Analisis Jaringan Sosial (NodeXL Co-commenting SNA)
./bit analyze all             # Pembangunan graf, modularitas Louvain (5 klaster), dan visualisasi

# 4. Analisis Korelasi & Pemodelan Prediksi
./bit correlate               # Uji permutasi eksak Spearman vs box office bersumber
./bit rebuild-master          # Rekonstruksi tabel bersih (purge seluruh angka tak bersumber)
./bit model                   # Evaluasi LOOCV (Leave-One-Out Cross-Validation) MAPE
./bit robust                  # Uji ketahanan bootstrap 95%, koreksi Benjamini-Hochberg & parsial
./bit finish                  # Alur terpadu satu perintah: predict -> validate -> analyze -> correlate

# 5. Paket Publikasi Ilmiah & Dashboard
./bit package                 # Pembuatan paket data rilis ber-checksum SHA-256 (Scopus Q1)
./bit dashboard               # Menjalankan antarmuka web explorer interaktif
```

---

## 🌐 Dashboard Eksplorasi Interaktif

Repositori ini menyertakan web dashboard visual premium berbasis Dark-Glassmorphism (`dashboard/index.html` dan `dashboard/data.json`):
- **Master Data & Provenance:** Eksplorasi tabel data bersih 15 film lengkap dengan status finalitas dan modal tautan sumber rujukan.
- **Deep-Dive per Film:** Visualisasi overlay perbandingan views, likes, dan distribusi sentimen IndoBERT vs Leksikon Emoji.
- **Analisis Lintas Film (RQ1–RQ4):** Scatter plot interaktif korelasi Spearman dan distribusi klaster komunitas NodeXL.
- **Simulator Prediksi Penonton:** Kalkulator estimasi perolehan tiket bioskop dengan memasukkan sinyal pra-rilis trailer dan faktor waralaba/musim.
- **Audit & Metodologi:** Panduan perintah CLI dan ringkasan kepatuhan etika.

---

## 🔒 Etika Penelitian & Kepatuhan Regulasi (UU PDP No. 27/2022)

Penelitian ini mematuhi **Undang-Undang Republik Indonesia Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi**:
1. **Anonimisasi Kriptografis (Pseudonimisasi):** Seluruh identitas komentator (`author_id` / `channel_id`) disamarkan menjadi pengenal acak menggunakan algoritma **HMAC-SHA256** dengan salt rahasia (`SORAYA_SALT`).
2. **Kerahasiaan Salt:** Salt tidak pernah dipublikasikan di repositori publik, memastikan proses hashing bersifat satu arah dan tidak dapat direkayasa balik (*irreversible*).
3. **Penyaringan PII Publik:** Berkas distribusi publik dan repositori git mengecualikan teks mentah komentar dan ID komentar unik YouTube.

---

## 📄 Struktur Repositori

```
├── AUDIT_REPORT.md             # Laporan audit ilmiah, signifikansi statistik, & integritas data
├── README.md                   # Dokumentasi komprehensif repositori riset
├── bit                         # CLI eksekutor terpadu (executable bash/python)
├── requirements.txt            # Dependensi pustaka Python (torch, transformers, yt-dlp, pytrends, networkx)
├── films.csv                   # Tanggal rilis bioskop dan kata kunci Google Trends
├── ids_soraya.txt              # Daftar video ID trailer resmi Soraya Intercine Films
├── ids_hitmaker.txt            # Daftar video ID trailer resmi Hitmaker Studios
├── ids_md.txt                  # Daftar video ID trailer resmi MD Pictures
├── analyze_youtube.py          # Analisis metrik YouTube, SNA, dan visualisasi grafik
├── correlate_films.py          # Korelasi Spearman permutasi eksak & audit konsistensi
├── sentiment_indobert.py       # Klasifikasi sentimen IndoBERT RoBERTa di Apple Silicon MPS
├── emoji_sentiment.py          # Leksikon polaritas emoji khusus bahasa Indonesia
├── paper_tools.py              # Utilitas penyusunan paket paper ilmiah (LOOCV, bootstrap, package)
├── dashboard/
│   ├── index.html              # Antarmuka web dashboard interaktif
│   └── data.json               # Basis data JSON terpadu (15 film terverifikasi)
├── data/
│   ├── films_clean.csv         # Master data bersih (semua terukur & bersumber resmi)
│   ├── box_office_sources.csv  # Log audit sumber penonton ber-URL dan tanggal akses
│   └── trends/                 # Data historis Google Trends Indonesia
├── release/                    # Paket reproduksi artikel ilmiah ber-checksum SHA-256
└── results/                    # Laporan keluaran analisis berkala & grafik visual
```

---

## 📜 Lisensi & Sitasi

Proyek ini dirilis di bawah lisensi **MIT License**.  
Bagi peneliti yang menggunakan dataset atau metodologi ini dalam karya ilmiah, silakan merujuk ke publikasi:

```bibtex
@article{kartika2026soraya,
  author    = {Kartika, Indri},
  title     = {Predicting Indonesian Theatrical Box Office Performance from Pre-Release YouTube Trailer Signals, Social Network Topology, and IndoBERT Sentiment},
  year      = {2026},
  journal   = {Preprint / Working Paper},
  url       = {https://github.com/indri007/soraya-film-explorer}
}
```
