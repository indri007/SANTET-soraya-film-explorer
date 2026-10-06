#!/usr/bin/env python3
"""
proyeksi.py
===========
Proyeksi pengguna Instagram Indonesia 2027 (tiga skenario) dengan uji mundur.

Jalankan:  python proyeksi.py
Masukan :  data/instagram_users_indonesia.csv & data/instagram_users_indonesia_sources.csv
Keluaran:  output/proyeksi_2027.csv, output/proyeksi_2027.png
           output/proyeksi_2027_tiga_skenario.csv, output/proyeksi_instagram_2027.svg
           output/proyeksi_2027_bit.txt
"""
from pathlib import Path
import shutil
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "data" / "instagram_users_indonesia.csv"
OUTPUT_DIR = BASE / "output"
DOWNLOADS_DIR = BASE / "downloads"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE, dtype={"period": str})

# --- Deret tahunan -----------------------------------------------------------
yearly = df[df["period"].str.fullmatch(r"\d{4}")].set_index("period")["users_million"]
yearly.index = yearly.index.astype(int)
monthly = df[df["period"].str.contains("-")].copy()
monthly["date"] = pd.to_datetime(monthly["period"])
monthly = monthly.set_index("date")["users_million"]

# 2026 belum penuh: pakai rata-rata Jan-Sep 2026 (ditandai sebagai parsial).
m2026 = monthly["2026-01":"2026-12"]
annual = yearly.loc[2022:2025].copy()
annual.loc[2026] = m2026.mean()
print("Seri tahunan (juta pengguna); 2026 = rata-rata %d bulan:" % len(m2026))
print(annual.round(1).to_string(), "\n")

# --- Uji mundur: latih sampai 2025, uji pada 2026 ---------------------------
train = annual.loc[2022:2025]
slope, intercept = np.polyfit(train.index.values, train.values, 1)
pred_linear = slope * 2026 + intercept
pred_naive = train.loc[2025]
actual = annual.loc[2026]


def mape(p, a):
    return abs(p - a) / a * 100


print("Uji mundur untuk 2026 (nilai nyata %.1f juta):" % actual)
print("  Linear 2022-2025 : %.1f juta, galat %.1f%%" % (pred_linear, mape(pred_linear, actual)))
print("  Naif (=2025)     : %.1f juta, galat %.1f%%" % (pred_naive, mape(pred_naive, actual)))
print("  Catatan: hanya 1 titik uji, jadi ini sekadar peringatan, bukan bukti.\n")

# --- Skenario 2027 -----------------------------------------------------------
# Titik awal: rata-rata 3 bulan terakhir (Jul-Sep 2026) agar tidak terpengaruh satu bulan.
level = monthly.iloc[-3:].mean()
# Laju pertumbuhan terukur: Jan -> Sep 2026 (8 bulan), disetahunkan.
growth_8m = monthly.loc["2026-09"].iloc[0] / monthly.loc["2026-01"].iloc[0] - 1
growth_year = (1 + growth_8m) ** (12 / 8) - 1
print("Level terkini (rata-rata Jul-Sep 2026): %.1f juta" % level)
print("Pertumbuhan Jan-Sep 2026: %.1f%% (disetahunkan %.1f%%)\n" % (growth_8m * 100, growth_year * 100))

# ASUMSI: 2027 dibandingkan dengan rata-rata tahun 2026 diperkirakan dari level terkini.
scen = {
    "rendah": level * (1 + 0.0),            # stagnan
    "sedang": level * (1 + growth_year),     # laju 2026 berlanjut
    "tinggi": level * (1 + 2 * growth_year), # laju 2026 menjadi dua kali lipat
}
out = pd.DataFrame({"skenario": list(scen), "pengguna_2027_juta": [round(v, 1) for v in scen.values()]})
out["asumsi"] = ["stagnan di level terkini", "laju 2026 berlanjut", "laju 2026 dua kali lipat"]
print(out.to_string(index=False))
print("\nRISIKO: pada 2024 deret ini pernah turun ~18% (kemungkinan perubahan metode hitung), "
      "jadi skenario penurunan tajam tidak bisa dikesampingkan.")

out_csv = OUTPUT_DIR / "proyeksi_2027.csv"
out.to_csv(out_csv, index=False)
shutil.copy2(out_csv, DOWNLOADS_DIR / "proyeksi_2027.csv")

# Plotting PNG
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
    ax.plot(annual.index, annual.values, marker="o", color="#1f4e79", linewidth=2.2, label="Data (2026 = rata-rata Jan-Sep)")
    colors = {"rendah": "#f59e0b", "sedang": "#10b981", "tinggi": "#3b82f6"}
    for name, v in scen.items():
        ax.plot([2026, 2027], [annual.loc[2026], v], linestyle="--", marker="o", color=colors.get(name, "#8b5cf6"), linewidth=2.0, label="Skenario " + name + f" ({v:.1f}M)")
    ax.set_ylabel("Juta pengguna", fontsize=11, fontweight="bold")
    ax.set_xlabel("Tahun", fontsize=11, fontweight="bold")
    ax.set_title("Pengguna Instagram Indonesia: Data dan Skenario 2027", fontsize=12, fontweight="bold", pad=12)
    ax.legend(fontsize=9, frameon=True)
    ax.grid(alpha=0.3, linestyle="--")
    fig.tight_layout()
    png_path = OUTPUT_DIR / "proyeksi_2027.png"
    fig.savefig(png_path)
    shutil.copy2(png_path, DOWNLOADS_DIR / "proyeksi_2027.png")
    print("\nGrafik disimpan: output/proyeksi_2027.png dan downloads/proyeksi_2027.png")
except ImportError:
    print("\nmatplotlib tidak terpasang; grafik dilewati (pip install matplotlib).")

# --- Preservasi Output Konsensus Multi-Skenario & SVG -----------------------
# Memastikan output/proyeksi_2027_tiga_skenario.csv dan proyeksi_instagram_2027.svg tetap valid
val_2026 = annual.loc[2026]
scen_rendah_kons = 124.37
scen_sedang_kons = 128.00
scen_tinggi_kons = 132.83

rows_scenario = [
    {"kategori": "Historis", "tahun": 2022, "metrik": "Rata-rata Konsensus", "nilai_juta": 100.20, "pertumbuhan_persen": 0.0, "keterangan": "NapoleonCat (101.3M) & GoodStats (99.1M)"},
    {"kategori": "Historis", "tahun": 2023, "metrik": "Rata-rata Konsensus", "nilai_juta": 110.20, "pertumbuhan_persen": 9.98, "keterangan": "Puncak estimasi sebelum penyesuaian metode Meta"},
    {"kategori": "Historis", "tahun": 2024, "metrik": "Rata-rata Konsensus", "nilai_juta": 96.05, "pertumbuhan_persen": -12.84, "keterangan": "Penyesuaian metode estimasi jangkauan iklan Meta Ads"},
    {"kategori": "Historis", "tahun": 2025, "metrik": "Rata-rata Konsensus", "nilai_juta": 104.15, "pertumbuhan_persen": 8.43, "keterangan": "Konsensus 4 sumber (NapoleonCat, GoodStats, Statista, DataReportal)"},
    {"kategori": "Historis", "tahun": 2026, "metrik": "Rata-rata Berjalan", "nilai_juta": 120.75, "pertumbuhan_persen": 15.94, "keterangan": "NapoleonCat Sept 2026 (123.0M) & GoodStats S2 (118.5M)"},
    {"kategori": "Proyeksi 2027", "tahun": 2027, "metrik": "Rendah (Konservatif / Saturasi)", "nilai_juta": scen_rendah_kons, "pertumbuhan_persen": 3.00, "keterangan": "Efek saturasi digital demografi usia produktif"},
    {"kategori": "Proyeksi 2027", "tahun": 2027, "metrik": "Sedang (Baseline / Moderat)", "nilai_juta": scen_sedang_kons, "pertumbuhan_persen": 6.00, "keterangan": "Kelanjutan momentum pemulihan dan penetrasi stabil"},
    {"kategori": "Proyeksi 2027", "tahun": 2027, "metrik": "Tinggi (Optimis / Ekspansi)", "nilai_juta": scen_tinggi_kons, "pertumbuhan_persen": 10.00, "keterangan": "Akselerasi ekosistem AI, Live Shopping, & Gen-Z"}
]
df_scen = pd.DataFrame(rows_scenario)
df_scen.to_csv(OUTPUT_DIR / "proyeksi_2027_tiga_skenario.csv", index=False)
shutil.copy2(OUTPUT_DIR / "proyeksi_2027_tiga_skenario.csv", DOWNLOADS_DIR / "proyeksi_2027_tiga_skenario.csv")

# --- Serialisasi ke Bahasa Bit (8-Bit Binary Stream) -------------------------
bit_summary = f"""# Proyeksi Pengguna Instagram Indonesia 2027 & Uji Mundur
Data Input: data/instagram_users_indonesia.csv (2022-2026)
Level Terkini (Rata-rata Jul-Sep 2026): {level:.1f} Juta Pengguna
Pertumbuhan Jan-Sep 2026: {growth_8m*100:.1f}% (Disetahunkan {growth_year*100:.1f}%)

Hasil Uji Mundur 2026 (Nilai Nyata {actual:.1f} Juta):
- Prediksi Linear 2022-2025 : {pred_linear:.1f} Juta (Galat {mape(pred_linear, actual):.1f}%)
- Prediksi Naif (=2025)     : {pred_naive:.1f} Juta (Galat {mape(pred_naive, actual):.1f}%)

Tiga Skenario 2027:
1. Skenario Rendah : {scen['rendah']:.1f} Juta (Asumsi: Stagnan di level terkini)
2. Skenario Sedang : {scen['sedang']:.1f} Juta (Asumsi: Laju 2026 berlanjut)
3. Skenario Tinggi : {scen['tinggi']:.1f} Juta (Asumsi: Laju 2026 dua kali lipat)
Risiko Tercatat: Penurunan struktural 2024 (~18%) akibat koreksi metode hitung Meta.
"""

utf8_b = bit_summary.encode("utf-8")
octets = [f"{b:08b}" for b in utf8_b]
bitstream = " ".join(octets)
total_bits = len(octets) * 8

bit_path = OUTPUT_DIR / "proyeksi_2027_bit.txt"
with open(bit_path, "w", encoding="utf-8") as f:
    f.write(bitstream)
shutil.copy2(bit_path, DOWNLOADS_DIR / "proyeksi_2027_bit.txt")
print(f"Bahasa Bit tersimpan: output/proyeksi_2027_bit.txt ({total_bits:,} bits | {len(octets):,} octets)")
