#!/usr/bin/env bash
# run_scrape.sh — Pengumpulan data komentar YouTube (Soraya & Ivanna) via yt-dlp
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# 1. Pastikan virtual environment aktif
if [ ! -d ".venv" ]; then
    echo "[*] Membuat virtual environment .venv..."
    /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -m venv .venv
fi
source .venv/bin/activate

echo "[*] Memperbarui yt-dlp dan pandas..."
pip install -q -U yt-dlp pandas certifi

export SORAYA_SALT="${SORAYA_SALT:-kalimat-rahasia-yang-sama-terus}"

echo ""
echo "============================================================"
echo "1) Pengumpulan Trailer Resmi Soraya & Hitmaker (ids_soraya.txt)"
echo "============================================================"
python -m yt_dlp -a ids_soraya.txt --ignore-errors \
  --skip-download --write-info-json --write-comments \
  --extractor-args "youtube:max_comments=${MAX_COMMENTS:-all},all,all,all" \
  --sleep-requests 1 --sleep-interval 3 --max-sleep-interval 8 \
  -o "yt_soraya/%(id)s.%(ext)s" --force-overwrites

echo "[*] Mengonversi yt_soraya menjadi CSV & NodeXL network..."
python ytdlp_to_csv.py yt_soraya --salt "$SORAYA_SALT"

echo ""
echo "============================================================"
echo "2) Pengumpulan Ivanna (MD Pictures - Pembanding Non-Soraya)"
echo "============================================================"
python -m yt_dlp -a ids_ivanna.txt --ignore-errors \
  --skip-download --write-info-json --write-comments \
  --extractor-args "youtube:max_comments=${MAX_COMMENTS:-all},all,all,all" \
  --sleep-requests 1 --sleep-interval 3 --max-sleep-interval 8 \
  -o "yt_ivanna/%(id)s.%(ext)s" --force-overwrites

echo "[*] Mengonversi yt_ivanna menjadi CSV & NodeXL network..."
python ytdlp_to_csv.py yt_ivanna --salt "$SORAYA_SALT"

echo ""
echo "✅ Seluruh proses pengumpulan data selesai!"
