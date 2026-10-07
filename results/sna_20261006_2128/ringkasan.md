# SANTET · Analisis Jaringan Komentar YouTube

_06-10-2026 21:28 · 7,337 komentar · 5,653 akun (pseudonim) · 13 film · set: soraya, md_

## 01. Peta jaringan keseluruhan (komentator–film + balasan)

Simpul: 5,666 · sisi: 7,431. Gambar `01_peta.png` (dibatasi komentator dengan derajat tertinggi agar terbaca); graf penuh `01_peta.graphml` bisa dibuka di NodeXL/Gephi.

## 02. Group-in-a-Box: tiap komunitas dalam kotak sendiri

`02_grup-kotak.png` menampilkan 9 komunitas terbesar (maks. 400 simpul per kotak).

## 03. Graf balasan per film (small multiples)

`03_per-film.png` · angka di `03_per-film.csv`.

| film                                             |   simpul_balasan |   sisi_balasan |
|:-------------------------------------------------|-----------------:|---------------:|
| Suzzanna: Malam Jumat Kliwon (2023)              |              309 |            288 |
| Suzzanna: Santet Dosa di Atas Dosa (2026)        |              272 |            255 |
| Jurnal Risa by Risa Saraswati (2024)             |              179 |            163 |
| Janur Ireng: Sewu Dino Prequel (2025/2026)       |              136 |            107 |
| Suzzanna: Bernapas dalam Kubur (2018)            |              105 |             72 |
| Ivanna (2022)                                    |               53 |             50 |
| Badarawuhi di Desa Penari (2024)                 |               86 |             69 |
| Ipar Adalah Maut (2024)                          |               82 |             94 |
| Danur: The Last Chapter (2026)                   |               98 |             94 |
| Perewangan (2024)                                |              122 |            101 |
| Catatan Harian Menantu Sinting (2024)            |               71 |             49 |
| Racun Sangga: Santet Pemisah Rumah Tangga (2024) |               75 |             61 |
| Siccin 8                                         |                9 |              5 |

## 04. Graf berwarna kategori komentar (takut / niat menonton / lain)

`04_warna-niat.png` · `04_warna-niat.csv`. Kategori dari kata kunci, bukan model — perlu validasi label manusia.

| kategori        |   persen_komentar |
|:----------------|------------------:|
| lain            |              81.1 |
| takut (pujian?) |              11.7 |
| niat menonton   |               7.2 |

## 05. Proyeksi film–film: tebal garis = komentator bersama

`05_film-film.png` · `05_film-film.csv`

| film_a                                     | film_b                                     |   komentator_bersama |
|:-------------------------------------------|:-------------------------------------------|---------------------:|\
| Suzzanna: Malam Jumat Kliwon (2023)        | Suzzanna: Santet Dosa di Atas Dosa (2026)  |                   50 |
| Janur Ireng: Sewu Dino Prequel (2025/2026) | Suzzanna: Santet Dosa di Atas Dosa (2026)  |                   41 |
| Danur: The Last Chapter (2026)             | Suzzanna: Santet Dosa di Atas Dosa (2026)  |                   34 |
| Danur: The Last Chapter (2026)             | Janur Ireng: Sewu Dino Prequel (2025/2026) |                   26 |
| Janur Ireng: Sewu Dino Prequel (2025/2026) | Suzzanna: Malam Jumat Kliwon (2023)        |                   25 |
| Jurnal Risa by Risa Saraswati (2024)       | Suzzanna: Malam Jumat Kliwon (2023)        |                   18 |
| Suzzanna: Bernapas dalam Kubur (2018)      | Suzzanna: Malam Jumat Kliwon (2023)        |                   18 |
| Janur Ireng: Sewu Dino Prequel (2025/2026) | Jurnal Risa by Risa Saraswati (2024)       |                   15 |
| Jurnal Risa by Risa Saraswati (2024)       | Suzzanna: Santet Dosa di Atas Dosa (2026)  |                   13 |
| Ipar Adalah Maut (2024)                    | Suzzanna: Santet Dosa di Atas Dosa (2026)  |                   12 |

## 06. Densitas & komponen terhubung per film

`06_densitas.csv`. Densitas pada graf balasan per film.

| film                                             |   komentator |   sisi_balasan |   densitas |   komponen |   komponen_terbesar_% |   terisolasi_% |
|:-------------------------------------------------|-------------:|---------------:|-----------:|-----------:|----------------------:|---------------:|
| Suzzanna: Malam Jumat Kliwon (2023)              |         1421 |            288 |   0.000285 |       1160 |                  13.3 |           78.3 |\
| Suzzanna: Santet Dosa di Atas Dosa (2026)        |          985 |            255 |   0.000526 |        750 |                  19.6 |           72.4 |\
| Jurnal Risa by Risa Saraswati (2024)             |          650 |            163 |   0.000773 |        496 |                  15.7 |           72.5 |\
| Janur Ireng: Sewu Dino Prequel (2025/2026)       |          442 |            107 |   0.001098 |        336 |                   5.2 |           69.2 |\
| Suzzanna: Bernapas dalam Kubur (2018)            |          438 |             72 |   0.000752 |        367 |                   2.7 |           76   |\
| Badarawuhi di Desa Penari (2024)                 |          415 |             69 |   0.000803 |        348 |                   5.8 |           79.3 |\
| Ivanna (2022)                                    |          400 |             50 |   0.000627 |        353 |                   9.2 |           86.8 |\
| Ipar Adalah Maut (2024)                          |          353 |             94 |   0.001513 |        274 |                  22.1 |           76.8 |\
| Danur: The Last Chapter (2026)                   |          251 |             94 |   0.002996 |        164 |                  27.5 |           61   |\
| Perewangan (2024)                                |          246 |            101 |   0.003352 |        147 |                  13   |           50.4 |\
| Catatan Harian Menantu Sinting (2024)            |          234 |             49 |   0.001797 |        187 |                   4.7 |           69.7 |\
| Racun Sangga: Santet Pemisah Rumah Tangga (2024) |          168 |             61 |   0.004348 |        107 |                  22   |           55.4 |\
| Siccin 8                                         |           21 |              5 |   0.02381  |         16 |                  14.3 |           57.1 |\

## 07. Komunitas Louvain + modularitas Q

Louvain (seed 42) → 13 komunitas, modularitas **Q = 0.810** (struktur komunitas kuat). `07_komunitas.csv`

|   grup |   akun | film_dalam_grup                |
|-------:|-------:|:-------------------------------|
|      1 |   1346 | Suzzanna: Malam Jumat Kliwon   |
|      2 |    871 | Suzzanna: Santet Dosa di Atas… |
|      3 |    602 | Jurnal Risa by Risa Saraswati  |
|      4 |    420 | Suzzanna: Bernapas dalam Kubur |
|      5 |    402 | Badarawuhi di Desa Penari      |
|      6 |    399 | Janur Ireng: Sewu Dino Preque… |
|      7 |    392 | Ivanna                         |
|      8 |    343 | Ipar Adalah Maut               |
|      9 |    242 | Danur: The Last Chapter        |
|     10 |    229 | Perewangan                     |
|     11 |    225 | Catatan Harian Menantu Sinting |
|     12 |    163 | Racun Sangga: Santet Pemisah … |
|     13 |     19 | Siccin 8                       |

## 08. Irisan penonton antar-film (Jaccard)

280 dari 5,653 akun (5.0%) berkomentar di ≥2 film. `08_irisan.png` · `08_irisan.csv`

## 09. Akun jembatan antar-komunitas

Betweenness aproksimasi (k=400 sampel) pada graf komentator–film. `09_jembatan.csv`

| akun              |   betweenness |   komunitas_tersambung | film                                                                                                                               |
|:------------------|--------------:|-----------------------:|:-----------------------------------------------------------------------------------------------------------------------------------|
| user_4b396e2c580d |       0.03179 |                      6 | Badarawuhi di Desa …; Danur: The Last Cha…; Jurnal Risa by Risa…; Suzzanna: Malam Jum…; Suzzanna: Santet Do…                       |
| user_e6f7ec505c86 |       0.03003 |                      7 | Danur: The Last Cha…; Ipar Adalah Maut; Janur Ireng: Sewu D…; Perewangan; Suzzanna: Malam Jum…; Suzzanna: Santet Do…               |
| user_d618c596781b |       0.02142 |                      7 | Catatan Harian Mena…; Danur: The Last Cha…; Janur Ireng: Sewu D…; Jurnal Risa by Risa…; Racun Sangga: Sante…; Suzzanna: Santet Do… |
| user_698bfcf4f14c |       0.02049 |                      4 | Badarawuhi di Desa …; Catatan Harian Mena…; Jurnal Risa by Risa…; Suzzanna: Malam Jum…                                             |
| user_e25968070de7 |       0.01868 |                      5 | Danur: The Last Cha…; Ivanna; Janur Ireng: Sewu D…; Suzzanna: Santet Do…                                                           |
| user_b959d3fe7cc0 |       0.01738 |                      4 | Badarawuhi di Desa …; Jurnal Risa by Risa…; Racun Sangga: Sante…; Suzzanna: Malam Jum…                                             |
| user_4f749a01b43b |       0.01452 |                      4 | Badarawuhi di Desa …; Ivanna; Perewangan; Suzzanna: Bernapas …                                                                     |
| user_0c15c8c39ff1 |       0.01369 |                      4 | Ivanna; Perewangan; Suzzanna: Bernapas …; Suzzanna: Malam Jum…                                                                     |
| user_d950a1138663 |       0.01367 |                      3 | Jurnal Risa by Risa…; Suzzanna: Bernapas …; Suzzanna: Malam Jum…                                                                   |
| user_1c28f191697d |       0.01307 |                      4 | Ipar Adalah Maut; Suzzanna: Bernapas …; Suzzanna: Malam Jum…                                                                       |

## 10. Ukuran thread & persentase komentar yang dibalas

YouTube hanya punya satu tingkat balasan, jadi 'rantai' diukur sebagai ukuran thread. `10_rantai-balasan.csv`

| film                                             |   komentar_induk |   dibalas_pct |   rata_balasan |   thread_terpanjang |
|:-------------------------------------------------|-----------------:|--------------:|---------------:|--------------------:|
| Siccin 8                                         |               16 |          25   |           0.31 |                   2 |
| Danur: The Last Chapter (2026)                   |              222 |          20.7 |           0.33 |                   5 |
| Perewangan (2024)                                |              185 |          20.5 |           0.48 |                  18 |
| Racun Sangga: Santet Pemisah Rumah Tangga (2024) |              130 |          20   |           0.46 |                  15 |
| Suzzanna: Bernapas dalam Kubur (2018)            |              409 |          14.9 |           0.18 |                   4 |
| Catatan Harian Menantu Sinting (2024)            |              203 |          13.8 |           0.21 |                   8 |
| Janur Ireng: Sewu Dino Prequel (2025/2026)       |              404 |          13.6 |           0.21 |                  10 |
| Suzzanna: Santet Dosa di Atas Dosa (2026)        |              917 |          13.1 |           0.24 |                  18 |
| Jurnal Risa by Risa Saraswati (2024)             |              597 |          12.9 |           0.23 |                   9 |
| Badarawuhi di Desa Penari (2024)                 |              400 |          10.5 |           0.16 |                   4 |
| Ipar Adalah Maut (2024)                          |              326 |          10.4 |           0.28 |                  11 |
| Ivanna (2022)                                    |              400 |           8.5 |           0.13 |                   5 |
| Suzzanna: Malam Jumat Kliwon (2023)              |             1376 |           8.2 |           0.17 |                  28 |

## 11. Resiprositas balasan (saling membalas)

Proporsi sisi balasan yang dibalas balik. `11_resiprositas.csv`

| film                                             |   pasangan |   resiprositas |
|:-------------------------------------------------|-----------:|---------------:|
| SEMUA                                            |       1571 |         0.2088 |
| Badarawuhi di Desa Penari (2024)                 |         77 |         0.2078 |
| Catatan Harian Menantu Sinting (2024)            |         52 |         0.1154 |
| Danur: The Last Chapter (2026)                   |        107 |         0.243  |
| Ipar Adalah Maut (2024)                          |         98 |         0.0816 |
| Ivanna (2022)                                    |         65 |         0.4615 |
| Janur Ireng: Sewu Dino Prequel (2025/2026)       |        128 |         0.3281 |
| Jurnal Risa by Risa Saraswati (2024)             |        185 |         0.2378 |
| Perewangan (2024)                                |        110 |         0.1636 |
| Racun Sangga: Santet Pemisah Rumah Tangga (2024) |         65 |         0.1231 |
| Siccin 8                                         |          5 |         0      |
| Suzzanna: Bernapas dalam Kubur (2018)            |         79 |         0.1772 |
| Suzzanna: Malam Jumat Kliwon (2023)              |        321 |         0.2056 |
| Suzzanna: Santet Dosa di Atas Dosa (2026)        |        280 |         0.1786 |

## 12. Aktor paling aktif (out-degree)

`12_aktor-aktif.csv`

| akun              |   komentar+balasan_dibuat | film                                                                                                         |
|:------------------|--------------------------:|:-------------------------------------------------------------------------------------------------------------|
| user_a86f2cca6ce7 |                        36 | Danur: The Last C…; Janur Ireng: Sewu…; Racun Sangga: San…; Siccin 8; Suzzanna: Santet …                     |
| user_4b396e2c580d |                        29 | Badarawuhi di Des…; Danur: The Last C…; Jurnal Risa by Ri…; Suzzanna: Malam J…; Suzzanna: Santet …           |
| user_723d47d6bfef |                        29 | Janur Ireng: Sewu…; Suzzanna: Malam J…; Suzzanna: Santet …                                                   |
| user_1f8cdf894e6d |                        28 | Jurnal Risa by Ri…                                                                                           |
| user_4b7d675cdfe7 |                        26 | Ivanna                                                                                                       |
| user_86a771e04616 |                        26 | Ipar Adalah Maut                                                                                             |
| user_e6f7ec505c86 |                        16 | Danur: The Last C…; Ipar Adalah Maut; Janur Ireng: Sewu…; Perewangan; Suzzanna: Malam J…; Suzzanna: Santet … |
| user_7e8972108e68 |                        14 | Suzzanna: Bernapa…; Suzzanna: Malam J…; Suzzanna: Santet …                                                   |
| user_bf78f9042887 |                        14 | Suzzanna: Bernapa…; Suzzanna: Malam J…                                                                       |
| user_2768e357902b |                        13 | Ivanna; Jurnal Risa by Ri…                                                                                   |

## 13. Aktor paling banyak dibalas (in-degree)

`13_aktor-direspons.csv`

| akun              |   balasan_diterima | film                                                                                                         |
|:------------------|-------------------:|:-------------------------------------------------------------------------------------------------------------|
| user_e6f7ec505c86 |                 38 | Danur: The Last C…; Ipar Adalah Maut; Janur Ireng: Sewu…; Perewangan; Suzzanna: Malam J…; Suzzanna: Santet … |
| user_c6ff7e74e44f |                 28 | Suzzanna: Malam J…                                                                                           |
| user_d3c57408d206 |                 20 | Suzzanna: Santet …                                                                                           |
| user_4b7d675cdfe7 |                 19 | Ivanna                                                                                                       |
| user_7df7bd5916c3 |                 18 | Perewangan                                                                                                   |
| user_731461325f99 |                 17 | Suzzanna: Malam J…; Suzzanna: Santet …                                                                       |
| user_7246470f6590 |                 16 | Perewangan; Racun Sangga: San…                                                                               |
| user_38407c0ab8cb |                 15 | Perewangan                                                                                                   |
| user_7dc1bc16fc9b |                 15 | Suzzanna: Malam J…                                                                                           |
| user_17861810211f |                 12 | Badarawuhi di Des…                                                                                           |

## 14. Aktor perantara (betweenness)

Pada graf balasan (aproksimasi k=500). `14_perantara.csv`

| akun              |   betweenness | film                                                                                                         |
|:------------------|--------------:|:-------------------------------------------------------------------------------------------------------------|
| user_4b396e2c580d |      0.114182 | Badarawuhi di Des…; Danur: The Last C…; Jurnal Risa by Ri…; Suzzanna: Malam J…; Suzzanna: Santet …           |
| user_e6f7ec505c86 |      0.108917 | Danur: The Last C…; Ipar Adalah Maut; Janur Ireng: Sewu…; Perewangan; Suzzanna: Malam J…; Suzzanna: Santet … |
| user_a86f2cca6ce7 |      0.100751 | Danur: The Last C…; Janur Ireng: Sewu…; Racun Sangga: San…; Siccin 8; Suzzanna: Santet …                     |
| user_014f386718d1 |      0.061437 | Suzzanna: Malam J…; Suzzanna: Santet …                                                                       |
| user_731461325f99 |      0.048376 | Suzzanna: Malam J…; Suzzanna: Santet …                                                                       |
| user_86a771e04616 |      0.04439  | Ipar Adalah Maut                                                                                             |
| user_8501d77535ac |      0.042659 | Suzzanna: Santet …                                                                                           |
| user_1f8cdf894e6d |      0.041208 | Jurnal Risa by Ri…                                                                                           |
| user_723d47d6bfef |      0.038776 | Janur Ireng: Sewu…; Suzzanna: Malam J…; Suzzanna: Santet …                                                   |
| user_bd7e4f4108c6 |      0.038427 | Suzzanna: Bernapa…; Suzzanna: Santet …                                                                       |

## 15. Aktor inti (PageRank)

PageRank pada graf balasan berarah. `15_aktor-inti.csv`

| akun              |   pagerank | film                                                                                                         |
|:------------------|-----------:|:-------------------------------------------------------------------------------------------------------------|
| user_731461325f99 |   0.013136 | Suzzanna: Malam J…; Suzzanna: Santet …                                                                       |
| user_e6f7ec505c86 |   0.011629 | Danur: The Last C…; Ipar Adalah Maut; Janur Ireng: Sewu…; Perewangan; Suzzanna: Malam J…; Suzzanna: Santet … |
| user_35ab48d5937e |   0.011487 | Suzzanna: Malam J…                                                                                           |
| user_f84ac5a4dde8 |   0.010791 | Janur Ireng: Sewu…                                                                                           |
| user_465fa1a40e6a |   0.009724 | Janur Ireng: Sewu…                                                                                           |
| user_d3c57408d206 |   0.008158 | Suzzanna: Santet …                                                                                           |
| user_c6ff7e74e44f |   0.008042 | Suzzanna: Malam J…                                                                                           |
| user_a1b4393b6d96 |   0.006672 | Jurnal Risa by Ri…; Suzzanna: Santet …                                                                       |
| user_3d18d04dbebd |   0.005829 | Badarawuhi di Des…; Suzzanna: Malam J…                                                                       |
| user_9f2e0033092f |   0.005405 | Perewangan                                                                                                   |

## 16. Superfans: akun yang berkomentar di ≥3 film

67 akun berkomentar di ≥3 film. Pengganti 'akun resmi', karena data tidak menandai akun kanal/pemeran. `16_superfans.csv`

Film yang paling banyak didatangi superfans:

| film                                             |   komentar_superfans |
|:-------------------------------------------------|---------------------:|
| Suzzanna: Santet Dosa di Atas Dosa (2026)        |                  100 |
| Suzzanna: Malam Jumat Kliwon (2023)              |                   99 |
| Janur Ireng: Sewu Dino Prequel (2025/2026)       |                   58 |
| Danur: The Last Chapter (2026)                   |                   48 |
| Jurnal Risa by Risa Saraswati (2024)             |                   30 |
| Suzzanna: Bernapas dalam Kubur (2018)            |                   25 |
| Ivanna (2022)                                    |                   20 |
| Perewangan (2024)                                |                   17 |
| Ipar Adalah Maut (2024)                          |                   15 |
| Racun Sangga: Santet Pemisah Rumah Tangga (2024) |                   14 |

## 17. Kata teratas per film & per komunitas

`17_kata-teratas.csv`

| kelompok                                               | kata_teratas                                                                                                                                       |
|:-------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|
| film: Badarawuhi di Desa Penari (2024)                 | film(173), nonton(99), badarawuhi(83), kkn(78), desa(66), penari(55), lebih(41), cerita(41), horor(36), bagus(28), saya(27), mau(25)               |
| film: Catatan Harian Menantu Sinting (2024)            | radit(98), bang(52), film(39), adegan(21), nonton(18), peran(12), ariel(12), main(11), tatum(11), mau(9), punya(9), papa(9)                        |
| film: Danur: The Last Chapter (2026)                   | danur(123), film(80), lebaran(28), last(24), chapter(23), ivanna(20), bagus(17), risa(17), sampah(16), semoga(13), nonton(13), tayang(13)          |
| film: Ipar Adalah Maut (2024)                          | film(92), nonton(62), aris(59), ipar(58), rani(41), adalah(37), suami(28), adik(28), maut(28), rumah(28), bikin(27), selingkuh(26)                 |
| film: Ivanna (2022)                                    | film(175), nonton(107), ivanna(93), bagus(55), danur(46), keren(41), horor(38), lebih(31), filmnya(31), cerita(25), bioskop(25), bikin(25)         |
| film: Janur Ireng: Sewu Dino Prequel (2025/2026)       | film(93), sewu(67), dino(66), ireng(50), nonton(45), janur(43), bikin(37), kuncoro(34), jawa(29), tayang(29), kimo(29), bagus(26)                  |
| film: Jurnal Risa by Risa Saraswati (2024)             | film(129), nonton(127), risa(72), medium(50), keren(47), liat(36), jurnal(36), trailer(36), serem(34), teh(34), horor(31), bioskop(30)             |
| film: Perewangan (2024)                                | film(109), nonton(44), indonesia(32), horror(23), cerita(21), bagus(20), horor(19), tempat(19), filmnya(18), nessie(18), perewangan(17), lahir(16) |
| film: Racun Sangga: Santet Pemisah Rumah Tangga (2024) | film(67), nonton(36), kalimantan(22), bagus(19), horor(16), soraya(16), keren(15), cerita(14), baru(13), tayang(12), racun(12), santet(11)         |
| film: Siccin 8                                         | nonton(11), siccin(5), film(5), senayan(2), sabar(2), mau(2), udh(2), kaya(2), bang(2), tayang(2), hari(2), bioskop(2)                             |
| film: Suzzanna: Bernapas dalam Kubur (2018)            | film(144), luna(95), maya(70), nonton(59), mirip(49), suzzana(38), suzanna(37), bagus(34), suzzanna(31), filmnya(28), full(27), movie(22)          |
| film: Suzzanna: Malam Jumat Kliwon (2023)              | film(348), nonton(277), luna(187), keren(176), maya(114), suzanna(106), sabar(103), bagus(97), wajib(85), serem(85), horor(80), lebih(80)          |
| film: Suzzanna: Santet Dosa di Atas Dosa (2026)        | film(300), luna(154), nonton(116), maya(111), suzanna(108), mirip(94), keren(90), bagus(84), lebih(81), suzzana(81), reza(73), suzzanna(69)        |
| komunitas 1                                            | film(352), nonton(263), luna(187), keren(167), maya(115), suzanna(103), sabar(99), bagus(90), wajib(81), serem(81), lebih(78), horor(76)           |
| komunitas 2                                            | film(280), luna(139), nonton(109), maya(100), suzanna(97), mirip(92), keren(86), bagus(76), lebih(74), suzzana(71), reza(65), suzzanna(55)         |
| komunitas 3                                            | nonton(126), film(123), risa(64), keren(47), medium(46), horor(33), teh(33), liat(32), trailer(30), bioskop(30), jurnal(30), serem(29)             |
| komunitas 4                                            | film(139), luna(96), maya(69), nonton(62), mirip(46), suzzana(36), suzanna(36), bagus(33), suzzanna(30), filmnya(28), full(27), keren(26)          |
| komunitas 5                                            | film(173), nonton(104), badarawuhi(81), kkn(77), desa(63), penari(52), cerita(43), lebih(40), horor(37), bagus(32), saya(27), mau(26)              |
| komunitas 6                                            | film(99), sewu(60), dino(59), ireng(46), nonton(44), janur(39), bikin(32), kuncoro(32), tayang(28), bagus(26), santet(24), lebih(24)               |

## 18. Pasangan kata (bigram) teratas

`18_pasangan-kata.csv` · per film di `18_pasangan-kata-per-film.csv`. Bahan kandidat leksikon Watch Intent Index.

| pasangan         |   frekuensi |
|:-----------------|------------:|
| luna maya        |         293 |
| film horor       |         144 |
| nonton film      |          92 |
| wajib nonton     |          87 |
| sewu dino        |          73 |
| film horror      |          67 |
| nonton bioskop   |          60 |
| desa penari      |          60 |
| pengen nonton    |          59 |
| mau nonton       |          56 |
| soraya intercine |          48 |
| janur ireng      |          47 |
| sundel bolong    |          46 |
| film indonesia   |          45 |
| kkn desa         |          44 |
| harus nonton     |          42 |
| bang radit       |          42 |
| kak luna         |          41 |
| jumat kliwon     |          41 |
| kisah nyata      |          39 |

## 19. Emoji & tagar teratas

28.6% komentar memakai emoji. `19_emoji-tagar.csv`

| jenis   | item   |   frekuensi |
|:--------|:-------|------------:|
| emoji   | 😂     |         672 |
| emoji   | ❤️      |         593 |
| emoji   | 😭     |         347 |
| emoji   | 😅     |         286 |
| emoji   | 👍     |         236 |
| emoji   | 🎉     |         221 |
| emoji   | 🔥     |         210 |
| emoji   | 😢     |         178 |
| emoji   | 😊     |         170 |
| emoji   | 🤣     |         147 |
| emoji   | 😮     |         125 |
| emoji   | 😍     |         110 |
| emoji   | 🏻     |          58 |
| emoji   | 🙏     |          55 |
| emoji   | 😁     |          52 |
| emoji   | 😱     |          46 |
| emoji   | 👏     |          44 |
| emoji   | 😜     |          40 |
| emoji   | 🤩     |          39 |
| emoji   | 🍍     |          35 |

## 20. Jaringan per jendela waktu (H-14, H-7, H-1, pasca-rilis)

Data YouTube API presisi tersedia di data/youtube_api/ — pertimbangkan memuatnya untuk analisis final. Film tanpa tanggal rilis di films_clean.csv dilewati. `20_waktu.csv`

| film                                             | jendela     |   komentar |   akun |   balasan |   niat_menonton_% |
|:-------------------------------------------------|:------------|-----------:|-------:|----------:|------------------:|
| Badarawuhi di Desa Penari (2024)                 | pasca-rilis |        500 |    415 |       100 |               6   |
| Catatan Harian Menantu Sinting (2024)            | pasca-rilis |        257 |    234 |        54 |               3.5 |
| Ipar Adalah Maut (2024)                          | pasca-rilis |        426 |    353 |       100 |               4.5 |
| Ivanna (2022)                                    | pasca-rilis |        500 |    400 |       100 |               4.4 |
| Jurnal Risa by Risa Saraswati (2024)             | pasca-rilis |        792 |    650 |       195 |              10.4 |
| Perewangan (2024)                                | < H-14      |        103 |     89 |        37 |               4.9 |
| Perewangan (2024)                                | pasca-rilis |        196 |    164 |        77 |               2   |
| Racun Sangga: Santet Pemisah Rumah Tangga (2024) | pasca-rilis |        198 |    168 |        68 |               3   |
| Suzzanna: Bernapas dalam Kubur (2018)            | pasca-rilis |        500 |    438 |        91 |               2.6 |
| Suzzanna: Malam Jumat Kliwon (2023)              | pasca-rilis |       1728 |   1421 |       352 |              12.6 |
| Suzzanna: Santet Dosa di Atas Dosa (2026)        | < H-14      |        750 |    636 |       166 |               6.1 |
| Suzzanna: Santet Dosa di Atas Dosa (2026)        | H-14..H-8   |        105 |     97 |        21 |               2.9 |
| Suzzanna: Santet Dosa di Atas Dosa (2026)        | pasca-rilis |        360 |    277 |       111 |               5   |
