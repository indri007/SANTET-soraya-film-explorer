# Paket Data & Kode — Riset Komentar Trailer Film Indonesia

Dibuat 06-10-2026 12:13 WIB.

## Isi
- `data/films_clean.csv` — metrik per film; penonton hanya dari sumber ber-URL (`code/data/box_office_sources.csv`).
- `data/comments_labels_no_text.csv` — label & metadata komentar **tanpa teks dan tanpa ID komentar**.
- `data/videos_*.csv` — metadata trailer publik.
- `results/` — hasil analisis, korelasi, uji ketahanan, model, validasi.
- `code/` — seluruh skrip pipeline (`bit`), daftar ID video, tanggal rilis.

## Etika
Data berasal dari komentar publik YouTube. Identitas komentator dipseudonimkan dengan HMAC-SHA256
dan kunci rahasia yang tidak dipublikasikan. Teks komentar dan ID komentar tidak dibagikan untuk
mencegah identifikasi ulang; peneliti dapat mengumpulkan ulang data dengan daftar ID video dan skrip di `code/`.

## Integritas
Checksum SHA-256 seluruh berkas ada di `MANIFEST.sha256`.
