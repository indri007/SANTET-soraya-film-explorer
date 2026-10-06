"""
01_cleaning.py
==============
Step 1 — Data Cleaning & Audit
Pipeline: Instagram Indonesia Viral Intelligence

Input : data/Review Instagram.csv  (1,000 rows | UserName, Review Text, Rating)
Output: output/ig_01_cleaned.csv
        output/ig_01_audit.json

Run:
    python src/01_cleaning.py
    python -m src.01_cleaning
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd

# ---------------------------------------------------------------------------
# Paths (robust, relative to repo root)
# ---------------------------------------------------------------------------
REPO       = Path(__file__).resolve().parent.parent
RAW_CSV    = REPO / "data" / "Review Instagram.csv"
OUT_CSV    = REPO / "output" / "ig_01_cleaned.csv"
AUDIT_JSON = REPO / "output" / "ig_01_audit.json"

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------
_RE_URL      = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_RE_MENTION  = re.compile(r"@\w+")
_RE_HASHTAG  = re.compile(r"#\w+")
_RE_EMOJI    = re.compile(
    "[\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F004-\U0001F0CF"
    "\U0001F910-\U0001F9FF"
    "\U00010000-\U0010FFFF"
    "]+",
    flags=re.UNICODE,
)
_RE_MULTI_WS = re.compile(r"\s+")


# ---------------------------------------------------------------------------
# Feature extractors (on original/raw text before cleaning)
# ---------------------------------------------------------------------------

def count_urls(text: str) -> int:
    return len(_RE_URL.findall(str(text)))

def count_mentions(text: str) -> int:
    return len(_RE_MENTION.findall(str(text)))

def count_hashtags(text: str) -> int:
    return len(_RE_HASHTAG.findall(str(text)))

def count_emojis(text: str) -> int:
    return len(_RE_EMOJI.findall(str(text)))


# ---------------------------------------------------------------------------
# Text cleaner
# ---------------------------------------------------------------------------

def clean_text(raw: Any) -> str:
    """Normalize and clean Indonesian review text.
    Preserves readable content; removes noise (URLs, mentions, emojis).
    """
    if not isinstance(raw, str) or not str(raw).strip():
        return ""
    text = unicodedata.normalize("NFC", str(raw))
    text = _RE_URL.sub(" ", text)
    text = _RE_MENTION.sub(" ", text)
    text = _RE_HASHTAG.sub(" ", text)
    text = _RE_EMOJI.sub(" ", text)
    text = _RE_MULTI_WS.sub(" ", text).strip()
    return text


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_raw(path: Path = RAW_CSV) -> pd.DataFrame:
    """Load CSV with encoding fallback. Does NOT modify source."""
    for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            return pd.read_csv(path, encoding=enc)
        except (UnicodeDecodeError, Exception):
            continue
    raise ValueError(f"Cannot read {path} with any known encoding.")


# ---------------------------------------------------------------------------
# Column standardization
# ---------------------------------------------------------------------------

_COL_MAP = {
    "username":    "username",
    "user_name":   "username",
    "review_text": "review_text",
    "reviewtext":  "review_text",
    "text":        "review_text",
    "content":     "review_text",
    "rating":      "rating",
    "score":       "rating",
    "stars":       "rating",
}

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        c.strip().lower().replace(" ", "_").replace("-", "_")
        for c in df.columns
    ]
    df = df.rename(columns={c: _COL_MAP.get(c, c) for c in df.columns})
    return df


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def audit_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    audit: dict[str, Any] = {
        "rows":             int(len(df)),
        "columns":          list(df.columns),
        "dtypes":           df.dtypes.astype(str).to_dict(),
        "null_counts":      df.isnull().sum().to_dict(),
        "null_total":       int(df.isnull().sum().sum()),
        "duplicate_rows":   int(df.duplicated().sum()),
    }
    if "review_text" in df.columns:
        audit["duplicate_text"] = int(df["review_text"].duplicated().sum())
        audit["empty_text"]     = int((df["review_text"].str.strip() == "").sum())
    if "rating" in df.columns:
        audit["rating_distribution"] = {
            str(k): int(v)
            for k, v in df["rating"].value_counts().sort_index().items()
        }
        audit["rating_dtype"]   = str(df["rating"].dtype)
        audit["rating_nulls"]   = int(df["rating"].isnull().sum())
    return audit


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run(verbose: bool = True) -> dict[str, Any]:
    """Full cleaning pipeline. Returns audit dict."""
    if verbose:
        print("=" * 60)
        print("01_cleaning.py | Instagram Indonesia Cleaning Pipeline")
        print(f"Input : {RAW_CSV}")
        print(f"Output: {OUT_CSV}")
        print("=" * 60)

    # 1. Load raw
    df = load_raw(RAW_CSV)
    if verbose:
        print(f"\n[LOAD]  {len(df):,} rows loaded | Columns: {list(df.columns)}")

    # 2. Standardize columns
    df = standardize_columns(df)
    required = {"username", "review_text", "rating"}
    missing_cols = required - set(df.columns)
    if missing_cols:
        raise ValueError(f"Required columns missing after standardization: {missing_cols}")
    if verbose:
        print(f"[COLS]  Standardized → {list(df.columns)}")

    # 3. Type coercion
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["username"] = df["username"].fillna("unknown").astype(str).str.strip()
    df["review_text"] = df["review_text"].fillna("").astype(str)

    # 4. Missing value audit (before drop)
    null_total = int(df.isnull().sum().sum())
    if verbose:
        print(f"[NULL]  {null_total} null values detected")

    # 5. Drop rows with null rating or empty text
    n_before = len(df)
    df = df[df["rating"].notna() & (df["review_text"].str.strip() != "")].copy()
    n_after = len(df)
    if verbose:
        print(f"[DROP]  {n_before - n_after} rows removed (null rating/empty text) → {n_after:,} rows")

    # 6. Duplicates
    n_dup = int(df.duplicated(subset=["review_text"]).sum())
    df = df.drop_duplicates(subset=["review_text"]).reset_index(drop=True)
    if verbose:
        print(f"[DUP]   {n_dup} duplicate text rows removed → {len(df):,} rows")

    # 7. Extract raw-text features (before cleaning text)
    df["url_count"]     = df["review_text"].apply(count_urls)
    df["mention_count"] = df["review_text"].apply(count_mentions)
    df["hashtag_count"] = df["review_text"].apply(count_hashtags)
    df["emoji_count"]   = df["review_text"].apply(count_emojis)

    # 8. Clean text
    df["clean_text"]  = df["review_text"].apply(clean_text)
    df["text_length"] = df["clean_text"].str.len()
    df["token_count"] = df["clean_text"].str.split().str.len().fillna(0).astype(int)
    if verbose:
        print("[TEXT]  Features added: url_count, mention_count, hashtag_count, emoji_count, clean_text, text_length, token_count")

    # 9. Rating as int
    df["rating"] = df["rating"].astype(int)

    # 10. Audit final
    audit = audit_dataframe(df)
    audit["source_file"] = str(RAW_CSV)
    audit["output_file"] = str(OUT_CSV)

    # 11. Save output
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    if verbose:
        print(f"\n[SAVE]  {OUT_CSV.name} → {OUT_CSV.stat().st_size:,} bytes")

    # 12. Save audit
    with open(AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False, default=str)
    if verbose:
        print(f"[AUDIT] {AUDIT_JSON.name} saved")
        print("\nRating distribution:")
        for k, v in sorted(audit.get("rating_distribution", {}).items()):
            bar = "█" * (v // 20)
            print(f"  Rating {k}: {v:4d}  {bar}")
        print(f"\n✓ 01_cleaning.py complete → {len(df):,} clean rows")

    return audit


if __name__ == "__main__":
    result = run(verbose=True)
    sys.exit(0)
