# Kamus Data (Data Dictionary) — Soraya Film Explorer
Pembaruan Terakhir: 2026-10-05

| Entitas | Nama Kolom | Tipe | Deskripsi & Validasi |
|---|---|---|---|
| `films` | `film_id` | TEXT (PK) | Slug unik film (mis. `suzzanna-2023`) |
| `films` | `judul` | TEXT | Judul resmi rilis bioskop Indonesia |
| `films` | `rumah_produksi` | TEXT | Soraya Intercine Films atau Hitmaker Studios |
| `films` | `tanggal_rilis` | DATE (YYYY-MM-DD) | Tanggal tayang perdana di bioskop |
| `films` | `tahun` | INTEGER | Tahun rilis |
| `films` | `genre` | TEXT | Genre utama film (Horror, Comedy/Drama) |
| `films` | `is_franchise` | INTEGER (0/1) | Flag apakah bagian dari IP/Waralaba (Suzzanna, The Doll) |
| `films` | `momen_rilis` | TEXT | Periode rilis (Lebaran, Akhir Tahun, Libur Sekolah, Reguler) |
| `box_office` | `penonton` | INTEGER | Jumlah tiket penonton tercatat |
| `box_office` | `source` | TEXT | Asal data (filmindonesia.or.id, Cinepoint, IG, berita) |
| `box_office` | `is_final` | INTEGER (0/1) | 1 jika film sudah turun layar; 0 jika masih tayang |
| `box_office` | `is_official_selected`| INTEGER (0/1) | 1 jika angka ini yang diprioritaskan untuk analisis riset |
| `trends_daily` | `skor` | REAL [0-100] | Indeks minat pencarian Google Trends Indonesia |
| `yt_snapshots` | `views` | INTEGER | Jumlah tayangan video trailer resmi |
| `yt_snapshots` | `days_relative_to_release` | INTEGER | Jarak hari snapshot ke tanggal rilis bioskop (mis. -7 = H-7) |
| `yt_comments` | `author_hash` | TEXT | Identitas komentator yang di-hash (kepatuhan UU PDP No. 27/2022) |
| `yt_comments` | `sentimen` | TEXT | Klasifikasi emosi (`positive`, `neutral`, `negative`) |
