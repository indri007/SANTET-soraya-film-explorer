from pathlib import Path
import pandas as pd

SOURCE = Path("data/Review Instagram.csv")
OUTPUT = Path("output/master_instagram.csv")

df = pd.read_csv(SOURCE)

# Normalisasi nama kolom
rename = {
    "UserName": "username",
    "Review Text": "original_text",
    "Rating": "rating",
}

df = df.rename(columns=rename)

# Pastikan kolom utama tersedia
required = [
    "username",
    "original_text",
    "rating",
]

for col in required:
    if col not in df.columns:
        df[col] = None

# Metadata provenance
df["source"] = "local_dataset"
df["source_file"] = str(SOURCE)
df["source_type"] = "provided_dataset"

# ID internal
df.insert(
    0,
    "record_id",
    [f"IG-{i:06d}" for i in range(1, len(df) + 1)]
)

# Kolom final
columns = [
    "record_id",
    "username",
    "original_text",
    "rating",
    "source",
    "source_file",
    "source_type",
]

df = df[columns]

# Hapus text kosong
df["original_text"] = df["original_text"].fillna("").astype(str)
df = df[df["original_text"].str.strip() != ""]

# Deduplicate berdasarkan teks
df = df.drop_duplicates(
    subset=["original_text"],
    keep="first"
)

OUTPUT.parent.mkdir(exist_ok=True)

df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 70)
print("MASTER INSTAGRAM DATASET")
print("=" * 70)
print(f"Rows       : {len(df):,}")
print(f"Columns    : {len(df.columns)}")
print(f"Target     : 10,000")
print(f"Remaining  : {max(0, 10000-len(df)):,}")
print(f"Output     : {OUTPUT}")

print()
print("Columns:")
for c in df.columns:
    print(f"  - {c}")

print()
print("Source:")
print(df["source"].value_counts())

print()
print("SELESAI")
