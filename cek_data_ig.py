from pathlib import Path
import pandas as pd
import json

ROOT = Path(".")
EXTENSIONS = {".csv", ".parquet", ".json", ".jsonl", ".xlsx"}

print("=" * 70)
print("CEK DATA INSTAGRAM - PROJECT INSTAGRAM 2027")
print("=" * 70)

files = [
    p for p in ROOT.rglob("*")
    if p.is_file()
    and p.suffix.lower() in EXTENSIONS
    and "instagram" in p.name.lower() or (
        p.is_file() and p.suffix.lower() in EXTENSIONS
    )
]

if not files:
    print("\n❌ Tidak ditemukan file dataset CSV/Parquet/JSON/JSONL/XLSX.")
    raise SystemExit

print(f"\n📁 File dataset ditemukan: {len(files)}\n")

for i, path in enumerate(files, 1):
    print(f"\n{'-'*70}")
    print(f"[{i}] {path}")

    try:
        ext = path.suffix.lower()

        if ext == ".csv":
            df = pd.read_csv(path, low_memory=False)

        elif ext == ".parquet":
            df = pd.read_parquet(path)

        elif ext == ".xlsx":
            df = pd.read_excel(path)

        elif ext == ".json":
            try:
                df = pd.read_json(path)
            except:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                df = pd.DataFrame(data)

        elif ext == ".jsonl":
            df = pd.read_json(path, lines=True)

        else:
            continue

        print(f"Rows       : {len(df):,}")
        print(f"Columns    : {len(df.columns)}")
        print(f"Size       : {path.stat().st_size / 1024 / 1024:.2f} MB")

        print("\nKolom:")
        print(", ".join(map(str, df.columns)))

        # Deteksi kolom Instagram
        cols_lower = {str(c).lower(): c for c in df.columns}

        possible = {
            "username": ["username", "user", "account", "handle", "owner"],
            "followers": ["followers", "follower_count", "followers_count"],
            "caption": ["caption", "text", "description"],
            "likes": ["likes", "like_count", "likes_count"],
            "comments": ["comments", "comment_count", "comments_count"],
            "views": ["views", "view_count", "plays"],
            "shares": ["shares", "share_count"],
            "saves": ["saves", "save_count"],
            "date": ["date", "datetime", "timestamp", "created_at", "published_at"],
            "country": ["country", "location", "country_code"],
            "hashtag": ["hashtags", "hashtag"],
        }

        detected = {}

        for key, candidates in possible.items():
            for c in candidates:
                if c in cols_lower:
                    detected[key] = cols_lower[c]
                    break

        print("\n🔎 Deteksi field:")
        for key, col in detected.items():
            print(f"  ✓ {key:12} -> {col}")

        if "followers" in detected:
            col = detected["followers"]

            followers = pd.to_numeric(
                df[col].astype(str).str.replace(",", "", regex=False),
                errors="coerce"
            )

            valid = followers.notna()

            print("\n👥 FOLLOWERS")
            print(f"  Valid follower data : {valid.sum():,}")
            print(f"  Followers >= 100   : {(followers >= 100).sum():,}")

            if valid.any():
                print(f"  Minimum             : {followers[valid].min():,.0f}")
                print(f"  Maximum             : {followers[valid].max():,.0f}")
                print(f"  Median              : {followers[valid].median():,.0f}")

        if "date" in detected:
            col = detected["date"]
            dates = pd.to_datetime(df[col], errors="coerce")

            if dates.notna().any():
                print("\n📅 PERIODE DATA")
                print(f"  Earliest : {dates.min()}")
                print(f"  Latest   : {dates.max()}")

                years = dates.dt.year.value_counts().sort_index()
                print("\n  Records per year:")
                for year, count in years.items():
                    print(f"    {year}: {count:,}")

        if "country" in detected:
            col = detected["country"]
            print("\n🌏 COUNTRY / LOCATION")
            print(df[col].astype(str).value_counts().head(15).to_string())

        # Instagram relevance check
        ig_keywords = [
            "caption", "instagram", "followers",
            "likes", "comments", "hashtags",
            "media", "views", "username"
        ]

        matched = [
            c for c in df.columns
            if any(k in str(c).lower() for k in ig_keywords)
        ]

        print("\n📊 Instagram-related columns:")
        if matched:
            print("  " + ", ".join(map(str, matched)))
        else:
            print("  ⚠️ Belum terlihat field Instagram yang jelas.")

    except Exception as e:
        print(f"❌ Gagal membaca: {e}")

print("\n" + "=" * 70)
print("SELESAI")
print("=" * 70)
