"""
santet_schema.py — Skema data SANTET + validator (hanya pandas, tanpa library tambahan).

Dipakai oleh:  ./bit validate
Sumber skema : header file nyata di repo (7 Okt 2026). Ubah di sini kalau kolom berubah.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

# ── definisi kolom ──────────────────────────────────────────────────────────
@dataclass
class Col:
    name: str
    kind: str                      # str | int | float | bool | date | enum
    required: bool = True          # boleh kosong?
    unique: bool = False
    pattern: str | None = None     # regex untuk str
    min: float | None = None
    max: float | None = None
    choices: tuple = ()            # untuk enum


@dataclass
class Table:
    name: str
    path_glob: str                 # relatif dari root repo
    cols: list[Col]
    rules: list = field(default_factory=list)   # fungsi(df) -> list[str]


USER_ID = r"^user_[0-9a-f]{12}$"

FILMS = Table(
    name="films",
    path_glob="data/films_clean.csv",
    cols=[
        Col("film_id", "str", unique=True, pattern=r"^[a-z0-9-]+-\d{4}$"),
        Col("film", "str", unique=True),
        Col("rumah_produksi", "str"),
        Col("tahun", "int", min=2010, max=2030),
        Col("genre", "str"),
        Col("momen_rilis", "str"),
        Col("is_franchise", "int", min=0, max=1),
        Col("is_final", "int", min=0, max=1),
        Col("tanggal_rilis", "date", required=False),
        Col("penonton", "int", min=0),
        Col("trailers", "int", min=0),
        Col("views_total", "int", min=0),
        Col("likes_total", "int", min=0),
        Col("comments", "float", required=False, min=0),
        Col("unique_commenters", "float", required=False, min=0),
        *[Col(f"net_{s}", "float", required=False, min=-1, max=1)
          for s in ("indobert", "gabungan", "leksikon_emoji", "emoji")],
        *[Col(f"pos_{s}", "float", required=False, min=0, max=1)
          for s in ("indobert", "gabungan", "leksikon_emoji", "emoji")],
        Col("semua_trailer_diunggah_setelah_rilis", "bool"),
        Col("trends_pra_rilis", "float", required=False, min=0),
        Col("source", "str"),
        Col("source_url", "str", pattern=r"^https?://"),
        Col("retrieved_at", "date"),
    ],
    rules=[
        lambda df: [f"baris {i}: unique_commenters > comments"
                    for i, r in df.iterrows()
                    if pd.notna(r["unique_commenters"]) and pd.notna(r["comments"])
                    and r["unique_commenters"] > r["comments"]],
    ],
)

VERTICES = Table(
    name="vertices",
    path_glob="results/sna_*/nodexl/vertices.csv",
    cols=[
        Col("Vertex", "str", unique=True),
        Col("Jenis", "enum", choices=("user", "film")),
        Col("Komunitas", "int", min=1),
        Col("Kategori", "enum", choices=("lain", "takut (pujian?)", "niat menonton", "film")),
        Col("Jumlah Film", "float", required=False, min=1),
    ],
    rules=[
        # privasi: setiap simpul user WAJIB hash anonim
        lambda df: [f"simpul user tidak anonim: {v!r}"
                    for v in df.loc[df["Jenis"] == "user", "Vertex"]
                    if not re.match(USER_ID, str(v))][:10],
    ],
)

EDGES = Table(
    name="edges",
    path_glob="results/sna_*/nodexl/edges.csv",
    cols=[
        Col("Vertex 1", "str", pattern=USER_ID),
        Col("Vertex 2", "str"),
        Col("Edge Weight", "int", min=1),
        Col("Relationship", "enum", choices=("komentar", "balasan")),
    ],
)

SNA_COMMANDS = [
    "peta", "grup-kotak", "per-film", "warna-niat", "film-film", "densitas",
    "komunitas", "irisan", "jembatan", "rantai-balasan", "resiprositas",
    "aktor-aktif", "aktor-direspons", "perantara", "aktor-inti", "superfans",
    "kata-teratas", "pasangan-kata", "emoji-tagar", "waktu",
]

TABLES = [FILMS, VERTICES, EDGES]


# ── validator ───────────────────────────────────────────────────────────────
def norm_film(name: str) -> str:
    """Satukan dua bentuk judul film di edges.csv ('FILM::Judul' == 'Judul')."""
    return str(name).removeprefix("FILM::").strip()


def _check_col(df: pd.DataFrame, c: Col) -> list[str]:
    errs: list[str] = []
    if c.name not in df.columns:
        return [f"kolom hilang: {c.name}"]
    s = df[c.name]
    empty = s.isna() | (s.astype(str).str.strip() == "")
    if c.required and empty.any():
        errs.append(f"{c.name}: {int(empty.sum())} nilai kosong (wajib terisi)")
    v = s[~empty]
    if c.unique and v.duplicated().any():
        errs.append(f"{c.name}: duplikat {v[v.duplicated()].head(3).tolist()}")
    if c.kind in ("int", "float"):
        num = pd.to_numeric(v, errors="coerce")
        bad = num.isna()
        if bad.any():
            errs.append(f"{c.name}: bukan angka {v[bad].head(3).tolist()}")
        if c.kind == "int" and ((num.dropna() % 1) != 0).any():
            errs.append(f"{c.name}: ada nilai pecahan, harus bilangan bulat")
        if c.min is not None and (num < c.min).any():
            errs.append(f"{c.name}: nilai < {c.min}")
        if c.max is not None and (num > c.max).any():
            errs.append(f"{c.name}: nilai > {c.max}")
    elif c.kind == "date":
        bad = pd.to_datetime(v, errors="coerce", utc=True).isna()
        if bad.any():
            errs.append(f"{c.name}: tanggal tidak valid {v[bad].head(3).tolist()}")
    elif c.kind == "bool":
        bad = ~v.astype(str).str.lower().isin({"true", "false", "1", "0"})
        if bad.any():
            errs.append(f"{c.name}: bukan boolean {v[bad].head(3).tolist()}")
    elif c.kind == "enum":
        bad = ~v.isin(c.choices)
        if bad.any():
            errs.append(f"{c.name}: di luar pilihan {sorted(set(v[bad]))[:5]}")
    if c.pattern:
        bad = ~v.astype(str).str.match(c.pattern)
        if bad.any():
            errs.append(f"{c.name}: tidak cocok pola {c.pattern} → {v[bad].head(3).tolist()}")
    return errs


def validate_table(t: Table, path: Path) -> list[str]:
    df = pd.read_csv(path, encoding="utf-8-sig")
    errs = [e for c in t.cols for e in _check_col(df, c)]
    if not any(e.startswith("kolom hilang") for e in errs):
        for rule in t.rules:
            errs += rule(df)
    return errs


def validate_sna_folder(folder: Path) -> tuple[list[str], list[str]]:
    """Kembalikan (errors, warnings) untuk satu folder results/sna_*."""
    errs, warns = [], []
    for n, slug in enumerate(SNA_COMMANDS, 1):
        png = folder / f"{n:02d}_{slug}.png"
        csvs = sorted(folder.glob(f"{n:02d}_*.csv"))
        if not png.exists() and not csvs:
            warns.append(f"analisis {n:02d} {slug}: tidak ada PNG maupun CSV")
        for c in csvs:
            try:
                df = pd.read_csv(c)
            except Exception as e:                       # noqa: BLE001
                errs.append(f"{c.name}: gagal dibaca ({e})")
                continue
            if df.empty:
                warns.append(f"{c.name}: kosong")
            elif df.select_dtypes("number").empty and not png.exists():
                warns.append(f"{c.name}: tidak ada kolom angka, grafik otomatis tidak bisa dibuat")
    if not (folder / "ringkasan.md").exists():
        warns.append("ringkasan.md tidak ada (catatan per analisis kosong)")

    # integritas relasi: semua ujung sisi harus ada di vertices
    v, e = folder / "nodexl/vertices.csv", folder / "nodexl/edges.csv"
    if v.exists() and e.exists():
        names = {norm_film(x) for x in pd.read_csv(v, encoding="utf-8-sig")["Vertex"]}
        ed = pd.read_csv(e, encoding="utf-8-sig")
        prefixed = ed["Vertex 2"].astype(str).str.startswith("FILM::").sum()
        if prefixed:
            warns.append(f"edges.csv: {prefixed} judul berawalan 'FILM::' (dinormalisasi otomatis)")
        ends = set(ed["Vertex 1"].map(norm_film)) | set(ed["Vertex 2"].map(norm_film))
        orphan = sorted(ends - names)
        if orphan:
            errs.append(f"edges.csv: {len(orphan)} ujung sisi tidak ada di vertices.csv, mis. {orphan[:3]}")
    return errs, warns
