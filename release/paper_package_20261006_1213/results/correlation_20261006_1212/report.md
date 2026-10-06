# Korelasi Metrik YouTube vs Penonton Bioskop

_Dibuat 06-10-2026 12:12 WIB · n = 10 film_

## Film yang dianalisis

| film                                             |   penonton |   is_final | source                             |   views_total |   unique_commenters |
|:-------------------------------------------------|-----------:|-----------:|:-----------------------------------|--------------:|--------------------:|
| Catatan Harian Menantu Sinting (2024)            |     713862 |          1 | filmindonesia.or.id                |       2151656 |                 234 |
| Indigo: What Do You See? (2023)                  |    1015231 |          1 | Wikipedia ID / filmindonesia.or.id |       3147375 |                 616 |
| Mata Batin (2017)                                |    1282557 |          1 | filmindonesia.or.id                |        542865 |                  83 |
| Racun Sangga: Santet Pemisah Rumah Tangga (2024) |     525034 |          0 | Pikiran Rakyat / IG Soraya         |       5359442 |                 168 |
| Sabrina (2018)                                   |    1337510 |          1 | filmindonesia.or.id                |        809423 |                 nan |
| Santet Segoro Pitu (2024)                        |    1025000 |          1 | IDN Times / Hitmaker Official      |       3773589 |                 369 |
| Suzzanna: Bernapas dalam Kubur (2018)            |    3346216 |          1 | filmindonesia.or.id                |       9647484 |                 438 |
| Suzzanna: Malam Jumat Kliwon (2023)              |    2189363 |          1 | Wikipedia EN / filmindonesia.or.id |       4869567 |                1421 |
| Suzzanna: Santet Dosa di Atas Dosa (2026)        |    1054864 |          0 | Cinepoint / IDN Times              |       3187674 |                 985 |
| The Doll 3 (2022)                                |    1764077 |          1 | Wikipedia EN / filmindonesia.or.id |       6679661 |                 535 |

Tidak masuk (tidak ada angka penonton bersumber): Badarawuhi di Desa Penari (2024), Danur: The Last Chapter (2026), Ipar Adalah Maut (2024), Ivanna (2022), Janur Ireng: Sewu Dino Prequel (2025/2026), Jurnal Risa by Risa Saraswati (2024), Perewangan (2024), Siccin 8

## Spearman (p-value eksak, permutasi)

| metrik             |   n |    rho |   p_exact |
|:-------------------|----:|-------:|----------:|
| views_total        |  10 |  0.333 |     0.351 |
| likes_total        |  10 |  0.6   |     0.072 |
| comments           |   9 |  0.417 |     0.27  |
| unique_commenters  |   9 |  0.417 |     0.27  |
| pos_indobert       |   9 |  0     |     1     |
| net_indobert       |   9 |  0.133 |     0.744 |
| pos_gabungan       |   9 |  0     |     1     |
| net_gabungan       |   9 |  0.067 |     0.88  |
| pos_leksikon_emoji |   9 |  0.133 |     0.744 |
| net_leksikon_emoji |   9 |  0.05  |     0.912 |
| pos_emoji          |   9 |  0.017 |     0.982 |
| net_emoji          |   9 | -0.05  |     0.912 |

Fitur pra-rilis: tidak tersedia (jalankan ./bit precise dengan YT_API_KEY). Film yang semua trailernya diunggah SETELAH rilis dikeluarkan dari fitur pra-rilis.

## ⚠️ Peringatan wajib dibaca

1. **n = 10 terlalu kecil untuk inferensi.** Dengan n = 10, p-value eksak terkecil yang mungkin adalah None; hasil apa pun **tidak bisa signifikan pada α = 0,05**. Gunakan hanya sebagai eksplorasi.
2. **Views/likes/komentar total diambil Oktober 2026**, bukan sebelum rilis — ada kebocoran waktu. Untuk prediksi, pakai fitur **pra-rilis** (komentar dengan tanggal tepat dari API). Timestamp yt-dlp ("3 years ago") TIDAK cukup presisi untuk itu.
3. **Penonton belum final** untuk film dengan `is_final = 0`.
4. **Sentimen belum tervalidasi** sampai `./bit sentiment validate` dijalankan dengan anotasi manual.

## Audit `data/films_master.csv`

Kolom `views_h7`, `comments_h7`, `sentiment_pos_ratio`, dll. di `films_master.csv` **tidak punya sumber**. 5 film punya `views_h7` (views 7 hari sebelum rilis) **lebih besar** daripada total views trailer saat ini — secara logika mustahil. Angka-angka tersebut, beserta hasil lama `rho = 0,9` dan `LOOCV MAPE` dari `./bit execute`, **tidak boleh dipakai di paper**. Rincian: `audit_films_master.csv`.
