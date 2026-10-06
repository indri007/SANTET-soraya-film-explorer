from pathlib import Path
import pandas as pd

ROOT = Path(".")
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "instagram2027",
    "output",
    "models",
    ".streamlit",
    "node_modules",
}

EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".json",
    ".jsonl",
    ".parquet",
}

print("=" * 70)
print("INSTAGRAM 2027 — RAW DATA SEARCH")
print("=" * 70)

found = []

for path in ROOT.rglob("*"):

    if not path.is_file():
        continue

    if path.suffix.lower() not in EXTENSIONS:
        continue

    if any(part in SKIP_DIRS for part in path.parts):
        continue

    try:
        suffix = path.suffix.lower()

        if suffix == ".csv":
            df = pd.read_csv(path, nrows=5)
            rows = sum(1 for _ in open(path, "r", encoding="utf-8-sig", errors="ignore")) - 1

        elif suffix in [".xlsx", ".xls"]:
            df = pd.read_excel(path, nrows=5)
            rows = len(pd.read_excel(path))

        elif suffix == ".json":
            df = pd.read_json(path)
            rows = len(df)

        elif suffix == ".jsonl":
            df = pd.read_json(path, lines=True)
            rows = len(df)

        elif suffix == ".parquet":
            df = pd.read_parquet(path)
            rows = len(df)

        else:
            continue

        columns = list(df.columns)

        text_candidates = [
            c for c in columns
            if any(k in str(c).lower()
                   for k in [
                       "text", "caption", "comment", "review",
                       "content", "description", "message"
                   ])
        ]

        username_candidates = [
            c for c in columns
            if any(k in str(c).lower()
                   for k in [
                       "username", "user", "author", "account"
                   ])
        ]

        instagram_candidates = [
            c for c in columns
            if any(k in str(c).lower()
                   for k in [
                       "instagram", "caption", "hashtag",
                       "reel", "comment", "username"
                   ])
        ]

        found.append({
            "file": str(path),
            "rows": rows,
            "columns": len(columns),
            "size_mb": round(path.stat().st_size / 1024 / 1024, 2),
            "text_fields": ", ".join(map(str, text_candidates)),
            "username_fields": ", ".join(map(str, username_candidates)),
            "instagram_fields": ", ".join(map(str, instagram_candidates)),
            "column_names": ", ".join(map(str, columns)),
        })

    except Exception as e:
        print(f"⚠️ Gagal membaca {path}: {e}")

print()
print("=" * 70)
print("HASIL RAW DATA DISCOVERY")
print("=" * 70)

if not found:
    print("❌ Tidak ditemukan dataset tambahan.")
else:
    total = 0

    for i, item in enumerate(found, 1):
        print()
        print(f"[{i}] {item['file']}")
        print(f"    Rows       : {item['rows']:,}")
        print(f"    Columns    : {item['columns']}")
        print(f"    Size       : {item['size_mb']} MB")
        print(f"    Text field : {item['text_fields'] or '-'}")
        print(f"    User field : {item['username_fields'] or '-'}")
        print(f"    IG fields  : {item['instagram_fields'] or '-'}")
        print(f"    Columns    : {item['column_names']}")

        total += item["rows"]

    print()
    print("=" * 70)
    print(f"FILE RAW DITEMUKAN : {len(found)}")
    print(f"TOTAL ROW RAW      : {total:,}")
    print("=" * 70)

    if total >= 10000:
        print("✅ Secara jumlah tersedia >= 10.000 rows.")
    else:
        print(f"❌ Masih kurang {10000-total:,} rows.")

    output = Path("output/raw_dataset_inventory.csv")
    output.parent.mkdir(exist_ok=True)

    pd.DataFrame(found).to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(f"Inventory disimpan: {output}")

print()
print("SELESAI")
