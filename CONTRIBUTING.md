# Aturan repo SANTET

Satu aturan di atas semuanya: **`./bit deploy` lulus, baru push ke `main`.**
Streamlit Cloud membaca `main` dan redeploy otomatis, jadi `main` harus selalu bisa jalan.

## 1. Alur kerja

| Langkah | Perintah |
| --- | --- |
| Mulai kerja | `git pull --rebase` |
| Cek cepat saat ngoding | `./bit web check` |
| Setelah mengubah data atau hasil SNA | `./bit validate` |
| Lihat hasilnya | `./bit web run` |
| Sebelum push | `./bit deploy` lalu `./bit deploy --push` |

Perubahan besar (lebih dari 1 file app) → branch `fitur/<nama>` → Pull Request → merge ke `main`.
Satu commit, satu maksud. Format pesan: `jenis: ringkasan` dengan jenis `feat` · `fix` · `data` · `style` · `docs`.

## 2. Aturan kode app

1. **Entrypoint satu:** `streamlit_app.py` hanya router `st.navigation`. Logika halaman ada di `streamlit_app/`.
2. **Path relatif ke file:** selalu `Path(__file__).resolve().parent / ...`. Dilarang `/Users/...`, `/home/...`, `C:\...`.
3. **Jangan import paket `streamlit_app`:** nama folder sama dengan file router. Modul bersama ditaruh di root (`santet_hero.py`, `santet_schema.py`).
4. **Baca data sekali:** bungkus `pd.read_csv` dengan `@st.cache_data`.
5. **Angka tidak diketik tangan:** angka di halaman dibaca dari `data/` atau `results/`. Kalau terpaksa diketik, beri catatan sumbernya di bawahnya.
6. **Halaman yang file-nya belum ada dilewati router**, jangan sampai app crash.
7. **Disclaimer wajib** di setiap halaman: tidak berafiliasi dengan Soraya, Hitmaker, MD Pictures.
8. **Dependensi app ringan:** hanya yang di `requirements.txt`. Library pipeline (torch, transformers, yt-dlp) masuk `requirements-pipeline.txt`.

## 3. Aturan desain (Material 3)

1. Semua warna, radius, dan font ada di `santet_m3.py` (token `--md-*`). Halaman tidak menulis hex baru.
2. Skema warna dibuat dari warna merek `#C2410C` dengan algoritme Material (fidelity, dark).
3. Teks kecil memakai `on-surface` / `on-surface-variant`; `primary-container` (#C2410C) hanya untuk latar chip dan angka besar.
4. Bentuk: hero 28 px, kartu 16 px, chip 8 px, tombol penuh (pill).
5. Gerak halus dan selalu menghormati `prefers-reduced-motion`.
6. Cek tampilan di lebar 390 px (ponsel) dan 1400 px sebelum push.

## 4. Aturan data

1. Skema resmi ada di `santet_schema.py`. Ubah kolom → ubah skema di commit yang sama.
2. Akun komentator **selalu** `user_` + 12 heksadesimal. Nama, handle, channel ID tidak boleh masuk repo.
3. Salt hash dari environment: `export SORAYA_SALT=<rahasia-acak-panjang>`. Tidak ada nilai default di kode.
4. Data mentah crawling (`yt_*/`, `*.info.json`) tetap di-ignore.
5. Setiap angka penonton punya `source`, `source_url`, `retrieved_at`.
6. Hasil SNA baru → folder baru `results/sna_<YYYYMMDD_HHMM>/`, jangan menimpa folder lama.
7. Data sintetis wajib diberi file penanda `SYNTHETIC_DATA.txt` di foldernya.

## 5. Aturan aset

| Aset | Batas | Cara |
| --- | --- | --- |
| `hero.mp4` | < 8 MB, 12 detik, tanpa audio | `./bit hero` |
| PNG grafik | < 5 MB per file | ekspor 150 dpi |
| File apa pun | < 100 MB (batas GitHub), peringatan di 50 MB | data besar ke HuggingFace |

File yang di-ignore tapi perlu ikut ke cloud: `git add -f <file>`. `./bit web check` akan memberi tahu.

## 6. Rahasia

`.streamlit/secrets.toml` dan `.env` tidak pernah di-commit. Rahasia untuk cloud diisi di **Streamlit Cloud → Settings → Secrets**, dibaca dengan `st.secrets["NAMA"]`.

## 7. Kebiasaan terminal (zsh di macOS)

- Kode Python **tidak** ditempel langsung ke terminal. Simpan ke file, lalu `python3 file.py`.
- Menulis file dari terminal pakai heredoc berkutip: `cat > file.py <<'EOF'` … `EOF` (kutip mencegah `!` dan `$` diproses zsh).
- Jangan menjalankan teks hasil decode langsung ke shell (`... | sh`). Baca dulu, baru jalankan.
- Selalu `cd` ke folder repo dulu sebelum perintah `git`.
