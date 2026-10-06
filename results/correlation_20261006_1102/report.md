# Korelasi Metrik YouTube vs Penonton Bioskop

_Dibuat 06-10-2026 11:02 WIB · n = 4 film_

## Film yang dianalisis

| film                                             |   penonton |   is_final | source                             |   views_total |   unique_commenters |
|:-------------------------------------------------|-----------:|-----------:|:-----------------------------------|--------------:|--------------------:|
| Catatan Harian Menantu Sinting (2024)            |     713862 |          1 | filmindonesia.or.id                |       2151656 |                 260 |
| Racun Sangga: Santet Pemisah Rumah Tangga (2024) |     525034 |          0 | Pikiran Rakyat / IG Soraya         |       5359442 |                 184 |
| Suzzanna: Malam Jumat Kliwon (2023)              |    2189363 |          1 | Wikipedia EN / filmindonesia.or.id |       4869567 |                1456 |
| Suzzanna: Santet Dosa di Atas Dosa (2026)        |    1054864 |          0 | Cinepoint / IDN Times              |       3187674 |                1040 |

Tidak masuk (tidak ada angka penonton bersumber): IVANNA (2022), Siccin 8

## Spearman (p-value eksak, permutasi)

| metrik             |   n |    rho |   p_exact |
|:-------------------|----:|-------:|----------:|
| views_total        |   4 | -0.2   |     0.917 |
| likes_total        |   4 |  0.8   |     0.333 |
| comments           |   4 |  1     |     0.083 |
| unique_commenters  |   4 |  1     |     0.083 |
| pos_indobert       |   4 |  0.8   |     0.333 |
| net_indobert       |   4 | -0.2   |     0.917 |
| pos_gabungan       |   4 |  0.8   |     0.333 |
| net_gabungan       |   4 |  0.4   |     0.75  |
| pos_leksikon_emoji |   4 |  0.738 |     0.333 |
| net_leksikon_emoji |   4 |  0     |     1     |
| pos_emoji          |   4 | -0.4   |     0.75  |
| net_emoji          |   4 | -0.4   |     0.75  |

## ⚠️ Peringatan wajib dibaca

1. **n = 4 terlalu kecil untuk inferensi.** Dengan n = 4, p-value eksak terkecil yang mungkin adalah 0.083; hasil apa pun **tidak bisa signifikan pada α = 0,05**. Gunakan hanya sebagai eksplorasi.
2. **Views/komentar diambil Oktober 2026, bukan H-7 sebelum rilis.** Metrik ini mencakup penonton setelah rilis (kebocoran waktu), sehingga korelasi dengan penonton cenderung terlalu tinggi.
3. **Penonton belum final** untuk film dengan `is_final = 0`.
4. **Sentimen belum tervalidasi** sampai `./bit sentiment validate` dijalankan dengan anotasi manual.

## Audit `data/films_master.csv`

Kolom `views_h7`, `comments_h7`, `sentiment_pos_ratio`, dll. di `films_master.csv` **tidak punya sumber**. 3 film punya `views_h7` (views 7 hari sebelum rilis) **lebih besar** daripada total views trailer saat ini — secara logika mustahil. Angka-angka tersebut, beserta hasil lama `rho = 0,9` dan `LOOCV MAPE` dari `./bit execute`, **tidak boleh dipakai di paper**. Rincian: `audit_films_master.csv`.
