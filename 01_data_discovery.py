from pathlib import Path
import pandas as pd
import json

ROOT = Path(".")
OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".json",
    ".jsonl",
    ".parquet",
}

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "instagram2027",
}

files = []

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    if any(part in SKIP_DIRS for part in path.parts):
        continue

    if path.suffix.lower() in EXTENSIONS:
        files.append(path)

print("=" * 70)
print("INSTAGRAM 2027 — DATA DISCOVERY")
print("=" * 70)

print(f"\nFiles ditemukan: {len(files)}\n")

inventory = []

for path in sorted(files):

    try:
        suffix = path.suffix.lower()

        if suffix == ".csv":
            df = pd.read_csv(path)

        elif suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(path)

        elif suffix == ".parquet":
            df = pd.read_parquet(path)

        elif suffix in [".json", ".jsonl"]:
            try:
                df = pd.read_json(path, lines=(suffix == ".jsonl"))
            except Exception:
                df = pd.read_json(path)

        else:
            continue

        size_mb = path.stat().st_size / (1024 * 1024)

        print("-" * 70)
        print(f"FILE       : {path}")
        print(f"ROWS       : {len(df):,}")
        print(f"COLUMNS    : {len(df.columns)}")
        print(f"SIZE       : {size_mb:.2f} MB")
        print("COLUMNS    :")
        print("  " + ", ".join(map(str, df.columns)))

        inventory.append({
            "file": str(path),
            "format": suffix,
            "rows": len(df),
            "columns": len(df.columns),
            "size_mb": round(size_mb, 3),
            "column_names": " | ".join(map(str, df.columns)),
        })

    except Exception as e:

        print("-" * 70)
        print(f"FILE       : {path}")
        print(f"ERROR      : {e}")

        inventory.append({
            "file": str(path),
            "format": path.suffix.lower(),
            "rows": None,
            "columns": None,
            "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
            "column_names": "",
            "error": str(e),
        })

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

inventory_df = pd.DataFrame(inventory)

if len(inventory_df):

    print(f"Total files : {len(inventory_df)}")
    print(f"Total rows  : {inventory_df['rows'].fillna(0).sum():,.0f}")

    output = OUTPUT / "data_inventory.csv"

    inventory_df.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nOutput:")
    print(output)

else:

    print("Tidak ditemukan dataset yang kompatibel.")

print("\nSELESAI")
