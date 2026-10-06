# Status Pipeline Paper — 06-10-2026 12:13 WIB

| Langkah | Status | Keterangan |
|---|---|---|
| 1. Komentar pra-rilis (API) | ⏳ | set YT_API_KEY lalu ulangi |
| 2. Validasi sentimen | ⏳ | annotator_1 baru 0 baris (butuh ≥30, saran 100–150) |
| 3. Perluas sampel film | ➖ | tidak ada set baru (4 set). Tambah: ./bit discover |
| 4. Data master bersumber | ✅ | data/films_clean.csv; kolom tanpa sumber dibuang |
| 5. Google Trends | ✅ | data/trends/ |
| 6. Sentimen final | ⚠️ | prediksi model dasar (belum tervalidasi); --with-llm tidak dipakai |
| 7. Model LOOCV | ✅ | results/model_*/ |
| 8. Uji ketahanan | ✅ | results/robust_*/ (bootstrap, Bonferroni, BH, parsial) |
| 9. Paket reproduksi | ✅ | release/paper_package_*/ (tanpa teks komentar) |
| 10. Draf metode + status | ✅ | results/paper_status.md |

## Draf bagian Data & Metode (angka terisi otomatis — periksa sebelum dipakai)

Data dikumpulkan dari 40 trailer dan teaser resmi pada kanal YouTube rumah produksi, mencakup 10 film (Hitmaker Studios, Hitmaker Studios (dist.) / Legacy Pictures, Hitmaker Studios (ko-produksi), Soraya Intercine Films). Sebanyak 9,840 komentar diambil menggunakan yt-dlp dengan batas 500 komentar per video, urutan terbaru. Identitas komentator dipseudonimkan dengan HMAC-SHA256. Jumlah penonton bioskop diambil dari sumber publik ber-URL; 10 film memiliki angka penonton terverifikasi.

Sentimen komentar diklasifikasikan dengan model RoBERTa bahasa Indonesia yang di-fine-tune pada SmSA (w11wo/indonesian-roberta-base-sentiment-classifier), leksikon domain dengan polaritas emoji, dan dua LLM lokal (qwen3:8b, gemma2:9b) sebagai anotator pembanding. [BELUM DIVALIDASI dengan anotasi manual — jangan klaim akurasi sentimen.] Hubungan metrik dengan penonton diuji dengan korelasi Spearman (uji permutasi eksak), bootstrap CI 95%, koreksi Benjamini–Hochberg, dan korelasi parsial dengan kontrol tahun rilis dan waralaba.

Model PREDIKTIF (fitur pra-rilis) dengan prediktor trends_pra_rilis dievaluasi secara leave-one-out (n = 9): MAPE 58.0% (CI95 [29.9, 90.6]) dibanding baseline rata-rata 52.8%. Model TIDAK lebih baik dari baseline.