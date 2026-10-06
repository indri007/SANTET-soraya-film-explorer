from pathlib import Path
import pandas as pd

ROOT = Path("data")

extensions = {
    ".csv",
    ".xlsx",
    ".xls",
    ".json",
    ".jsonl",
    ".parquet",
}

files = sorted(
    p for p in ROOT.rglob("*")
    if p.is_file() and p.suffix.lower() in extensions
)

print("=" * 70)
print("INSTAGRAM REELS DATASET AUDIT")
print("=" * 70)
print("FILES:", len(files))

for path in files:
    print("\n" + "-" * 70)
    print(path)

    try:
        if path.suffix == ".csv":
            df = pd.read_csv(path, nrows=5)
        elif path.suffix in {".xlsx", ".xls"}:
            df = pd.read_excel(path, nrows=5)
        elif path.suffix == ".json":
            df = pd.read_json(path)
            df = df.head(5)
        elif path.suffix == ".jsonl":
            df = pd.read_json(path, lines=True, nrows=5)
        elif path.suffix == ".parquet":
            df = pd.read_parquet(path).head(5)
        else:
            continue

        print("COLUMNS:")
        for c in df.columns:
            print("  -", c)

        print("SAMPLE ROWS:", len(df))

    except Exception as e:
        print("ERROR:", e)

print("\n" + "=" * 70)
print("AUDIT FINISHED")
print("=" * 70)
