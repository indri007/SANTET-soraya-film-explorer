from pathlib import Path
import pandas as pd
import re

# ============================================================
# CONFIG
# ============================================================

INPUT_DIR = Path("data")
OUTPUT_DIR = Path("output")

TARGET_ROWS = 10_000

OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# FIND CSV
# ============================================================

csv_files = list(INPUT_DIR.glob("*.csv"))

print("=" * 70)
print("INSTAGRAM 10,000 DATA PREPARATION")
print("=" * 70)

print(f"\n📁 Folder : {INPUT_DIR}")
print(f"📄 CSV ditemukan : {len(csv_files)}")

if not csv_files:
    print("❌ Tidak ada CSV di folder data/")
    raise SystemExit(1)

# ============================================================
# READ DATA
# ============================================================

frames = []

for file in csv_files:
    try:
        df = pd.read_csv(file)

        print(
            f"✓ {file.name:<35} "
            f"{len(df):>6,} rows | "
            f"{len(df.columns):>3} columns"
        )

        df["source_file"] = file.name
        frames.append(df)

    except Exception as e:
        print(f"⚠️ Gagal membaca {file.name}: {e}")

if not frames:
    print("❌ Tidak ada dataset yang berhasil dibaca.")
    raise SystemExit(1)

# ============================================================
# MERGE
# ============================================================

df = pd.concat(frames, ignore_index=True)

print("\n" + "-" * 70)
print("TOTAL RAW DATA")
print("-" * 70)

print(f"Rows : {len(df):,}")
print(f"Columns : {len(df.columns)}")

# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)

# Cari kolom teks
text_candidates = [
    "Review Text",
    "review_text",
    "text",
    "Text",
    "caption",
    "Caption",
    "content",
    "Content"
]

text_col = None

for col in text_candidates:
    if col in df.columns:
        text_col = col
        break

if text_col is None:
    print("\n❌ Kolom teks tidak ditemukan.")
    print("Kolom tersedia:")
    print(list(df.columns))
    raise SystemExit(1)

print(f"\n📝 Text column : {text_col}")

# ============================================================
# CLEAN TEXT
# ============================================================

df["clean_text"] = (
    df[text_col]
    .fillna("")
    .astype(str)
    .str.replace(r"http\S+", " ", regex=True)
    .str.replace(r"@\w+", " ", regex=True)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# ============================================================
# REMOVE EMPTY
# ============================================================

before = len(df)

df = df[df["clean_text"].str.len() >= 5].copy()

print(f"\n🧹 Empty/invalid text removed : {before - len(df):,}")

# ============================================================
# REMOVE DUPLICATE TEXT
# ============================================================

before = len(df)

df = df.drop_duplicates(
    subset=["clean_text"],
    keep="first"
).copy()

print(f"🔁 Duplicate text removed : {before - len(df):,}")

# ============================================================
# TEXT STATISTICS
# ============================================================

df["text_length"] = df["clean_text"].str.len()

# ============================================================
# LANGUAGE HEURISTIC
# ============================================================

def detect_language(text):

    text = text.lower()

    indo_words = [
        "yang", "dan", "ini", "itu", "dengan",
        "untuk", "tidak", "saya", "kamu",
        "bagus", "jelek", "sekali", "nya",
        "makan", "harga", "orang"
    ]

    score = sum(
        1 for word in indo_words
        if re.search(r"\b" + word + r"\b", text)
    )

    if score >= 2:
        return "id"

    return "unknown"


df["language"] = df["clean_text"].apply(detect_language)

# ============================================================
# KEEP TARGET
# ============================================================

if len(df) >= TARGET_ROWS:

    df = df.head(TARGET_ROWS).copy()

    status = "TARGET REACHED"

else:

    status = "TARGET NOT REACHED"

# ============================================================
# SAVE
# ============================================================

output_file = OUTPUT_DIR / "instagram_10000.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

# ============================================================
# REPORT
# ============================================================

print("\n" + "=" * 70)
print("FINAL RESULT")
print("=" * 70)

print(f"Target               : {TARGET_ROWS:,}")
print(f"Valid records        : {len(df):,}")
print(f"Remaining             : {max(0, TARGET_ROWS - len(df)):,}")
print(f"Status                : {status}")

print("\nLanguage:")
print(df["language"].value_counts(dropna=False))

print("\nText statistics:")
print(f"Mean length          : {df['text_length'].mean():.1f}")
print(f"Median length        : {df['text_length'].median():.1f}")
print(f"Minimum length       : {df['text_length'].min()}")
print(f"Maximum length       : {df['text_length'].max()}")

print("\n📦 Output:")
print(output_file)

print("\n" + "=" * 70)
