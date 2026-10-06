# PRD — Soraya Film Explorer (YouTube × Google Trends × Penonton)
**Tanggal:** 5 Okt 2026 · **Penulis:** @Indri

## 1. Ringkasan
Soraya Film Explorer adalah pipeline data + dashboard riset yang menggabungkan sinyal minat publik (YouTube dan Google Trends) dengan jumlah penonton bioskop film produksi Soraya Intercine Films dan Hitmaker Studios, periode 2020–2026. Tujuannya menjawab satu pertanyaan: **apakah minat online sebelum rilis bisa memprediksi jumlah penonton akhir?**

Latar belakang: Soraya Intercine Films (berdiri 1982) adalah salah satu rumah produksi tertua di Indonesia. Produksi horornya banyak dirilis lewat Hitmaker Studios, anak perusahaan yang didirikan keluarga Soraya. Waralaba Suzzanna menjadi aset utamanya; *Suzzanna: Malam Jumat Kliwon* (2023) meraih 2.189.363 penonton.

### Keluaran utama:
1. Dataset terstruktur (film, penonton, Google Trends, YouTube) yang bisa diunduh ulang
2. Dashboard eksplorasi per film dan lintas film
3. Model prediksi penonton berbasis sinyal pra-rilis
4. Bahan artikel ilmiah (target jurnal bereputasi)

---

## 2. Tujuan, Non-Goals & Metrik Sukses

### Pertanyaan Riset (Research Questions)
- **RQ1:** Seberapa kuat korelasi puncak Google Trends dan views trailer YouTube dengan total penonton film Soraya/Hitmaker?
- **RQ2:** Berapa hari sebelum rilis sinyal online mulai bisa memprediksi penonton (*lead time*)?
- **RQ3:** Apakah sentimen komentar trailer menambah daya prediksi di atas volume (views, search)?
- **RQ4:** Faktor apa yang membedakan film Soraya yang laris vs kurang laris (genre, IP lama, pemain, momen rilis)?

### Tujuan Produk
- Dataset bersih dan terdokumentasi untuk semua film rilis 2020–2026
- Pipeline pengumpulan otomatis yang bisa dijalankan ulang (*reproducible*)
- Dashboard untuk eksplorasi tren per film
- Model baseline prediksi penonton

### Non-Goals
- Tidak membangun produk komersial atau layanan publik
- Tidak mengambil data pribadi penonton atau komentator (nama/akun disamarkan)
- Tidak memprediksi pendapatan rupiah (data harga tiket tidak tersedia publik)

### Metrik Sukses
| Metrik | Target |
|---|---|
| Cakupan film 2020–2026 yang punya data lengkap | ≥ 90% |
| Kelengkapan data penonton terverifikasi ≥ 2 sumber | ≥ 80% film |
| Korelasi Spearman sinyal pra-rilis vs penonton | Dilaporkan + uji signifikansi |
| Error model (MAPE, leave-one-out) | Dilaporkan vs baseline naif |
| Pipeline dijalankan ulang tanpa edit manual | Ya |

---

## 3. Persona & User Stories

### Persona & Kebutuhan Utama
- **Peneliti (Indri):** Dataset valid + analisis statistik untuk artikel jurnal
- **Analis / Marketing Rumah Produksi:** Kapan dan di mana minat publik memuncak sebelum rilis
- **Reviewer Jurnal:** Metodologi yang transparan dan bisa direplikasi

### User Stories
- Sebagai peneliti, saya ingin satu tabel master film Soraya/Hitmaker 2020–2026 beserta penontonnya, agar punya variabel target yang konsisten.
- Sebagai peneliti, saya ingin skor Google Trends harian/mingguan per judul di jendela H-60 s.d. H+60, agar bisa mengukur lead time.
- Sebagai peneliti, saya ingin statistik trailer YouTube (views, likes, komentar) per film, agar bisa membandingkan antusiasme pra-rilis.
- Sebagai peneliti, saya ingin sentimen komentar trailer, agar bisa menguji RQ3.
- Sebagai analis, saya ingin grafik tren per film yang bisa ditumpuk (*overlay*) dengan tanggal rilis, agar pola terlihat sekilas.
- Sebagai reviewer, saya ingin log sumber data dan tanggal pengambilan untuk setiap angka, agar hasil bisa diverifikasi.

---

## 4. Ruang Lingkup Film & Data Penonton Awal
Cakupan awal: 7 film bioskop Soraya Intercine Films dan Hitmaker Studios rilis 2022–2026.

| Film | Rumah Produksi | Rilis Bioskop | Penonton (Angka Terakhir) | Status Angka | Sumber |
|---|---|---|---|---|---|
| Suzzanna: Santet Dosa di Atas Dosa | Soraya | 18 Mar 2026 (Lebaran) | 1.054.864 per 30 Mar 2026 | Sementara (masih tayang) | IDN Times / Cinepoint |
| Racun Sangga: Santet Pemisah Rumah Tangga | Soraya | 12 Des 2024 | 525.034 per hari ke-19 (1 Jan 2025) | Sementara | Pikiran Rakyat / IG Soraya |
| Santet Segoro Pitu | Hitmaker (ko-produksi) | Nov 2024 | > 1.000.000 (1.025.000 est) | Final belum ditemukan | IDN Times |
| Catatan Harian Menantu Sinting | Soraya | 18 Jul 2024 | 713.862 (filmindonesia) vs 783.899 (IG) | Konflik antar sumber | RRI / Pikiran Rakyat |
| Indigo: What Do You See? | Hitmaker (dist.) / Legacy Pictures | 19 Okt 2023 | 1.015.231 | Final | Wikipedia ID |
| Suzzanna: Malam Jumat Kliwon | Soraya | 3 Agu 2023 | 2.189.363 | Final | Wikipedia EN |
| The Doll 3 | Hitmaker | 26 Mei 2022 | 1.764.077 | Final | Wikipedia EN |

*Pembanding Historis (Pra-2020):*
- Suzzanna: Bernapas dalam Kubur (2018) — 3.346.216 (Soraya)
- Sabrina (2018) — 1.337.510 (Hitmaker)
- The Doll 2 (2017) — 1.226.864 (Hitmaker)
- Mata Batin (2017) — 1.282.557 (Hitmaker)

---

## 5. Skema Data (ERD Ringkas)
Semua tabel terhubung lewat `film_id`:
- `films`: Informasi master film, rumah produksi, genre, pemain, dsb.
- `box_office`: Multi-source data penonton bioskop (filmindonesia.or.id, Cinepoint, IG, berita, Wikipedia).
- `trends_daily`: Skor minat pencarian Google Trends (H-90 s.d. H+60) harian.
- `trends_region`: Skor regional per provinsi.
- `yt_videos`: Metadata video trailer/teaser resmi.
- `yt_snapshots`: Snapshot statistik video berkala (views, likes, comments).
- `yt_comments`: Komentar sampel (author di-hash, sentimen NLP).
- `support_metrics`: Rating IMDb/Letterboxd, Netflix Top 10, dsb.
