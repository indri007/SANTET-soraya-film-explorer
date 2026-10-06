# Panduan Anotasi Sentimen Komentar Trailer

Isi kolom `annotator_1` (anotator pertama) dan `annotator_2` (anotator kedua) dengan salah satu:
`positif`, `netral`, `negatif`. Kedua anotator bekerja **terpisah** dan tidak saling melihat jawaban.

| Label | Kapan dipakai | Contoh |
|---|---|---|
| positif | Pujian, antusias, ingin menonton, kagum — termasuk "serem banget" sebagai pujian film horor | "gila merinding, wajib nonton", "Luna Maya cantik banget" |
| negatif | Kritik, kecewa, mengejek, menolak menonton | "trailernya spoiler semua", "males, ceritanya itu-itu aja" |
| netral | Pertanyaan, info, tag teman, komentar di luar topik, campuran seimbang | "tayang tanggal berapa?", "@teman ayo", "first" |

Aturan tambahan:
1. Nilai **sikap terhadap film/trailer**, bukan topik. "Takut banget" pada film horor = positif bila nadanya kagum.
2. Sarkasme: labeli sesuai maksud sebenarnya.
   Emoji ikut dibaca: 😂🤣 bisa tawa senang atau mengejek; 😭😢 sering berarti terharu/ga sabar, bukan sedih.
3. Ragu di antara dua label → pilih `netral` dan tulis alasannya di kolom `catatan`.
4. Jangan membuka `_model_labels_hidden.csv` sebelum anotasi selesai.
