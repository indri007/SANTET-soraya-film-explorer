#!/usr/bin/env python3
"""
correlate_films.py — korelasi Spearman antara metrik YouTube HASIL SCRAPE (bukan angka manual)
dan jumlah penonton bioskop yang punya sumber (data/box_office_sources.csv, is_official_selected=1).

- p-value dihitung EKSAK dengan permutasi (cocok untuk n kecil), bukan pendekatan normal.
- Metrik sentimen diambil dari hasil terbaru ./bit sentiment predict (IndoBERT, gabungan, leksikon+emoji, emoji).
- Membandingkan juga kolom manual di data/films_master.csv dengan nilai hasil scrape (audit konsistensi).

Output: results/correlation_<stamp>/{film_features.csv, spearman.csv, audit_films_master.csv, report.md}
"""
import itertools
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from analyze_youtube import film_map, short_label, score  # noqa: E402


def norm(t):
    t = re.sub(r"\s*\(\d{4}\)\s*$", "", str(t))
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def spearman_exact(x, y):
    x, y = pd.Series(x).rank().values, pd.Series(y).rank().values
    n = len(x)

    def rho(a, b):
        ma, mb = a.mean(), b.mean()
        num = ((a - ma) * (b - mb)).sum()
        den = math.sqrt(((a - ma) ** 2).sum() * ((b - mb) ** 2).sum())
        return num / den if den else float("nan")

    r = rho(x, y)
    if n < 3 or math.isnan(r):
        return r, float("nan")
    if n <= 9:
        perms = [rho(x, y[list(p)]) for p in itertools.permutations(range(n))]
    else:
        import numpy as np
        rng = np.random.default_rng(42)
        perms = [rho(x, rng.permutation(y)) for _ in range(20000)]
    p = sum(abs(v) >= abs(r) - 1e-12 for v in perms) / len(perms)
    return r, p


def load_api_comments(fmap, title):
    """Komentar dari YouTube Data API (./bit precise) — punya tanggal publikasi TEPAT."""
    frames = []
    for d in sorted((BASE / "data" / "youtube_api").glob("*_*")):
        f = d / "comments.csv"
        if f.exists():
            c = pd.read_csv(f)
            c["api_run"] = d.name
            frames.append(c)
    if not frames:
        return None
    c = pd.concat(frames, ignore_index=True).drop_duplicates("comment_id", keep="last")
    c["published"] = pd.to_datetime(c.published_at, utc=True, errors="coerce")
    c["film"] = c.video_id.map(lambda v: short_label(fmap.get(v) or title.get(v, "")))
    return c


def main():
    # ---- penonton bersumber
    bo = pd.read_csv(BASE / "data" / "box_office_sources.csv")
    bo = bo[bo.is_official_selected == 1]
    master = pd.read_csv(BASE / "data" / "films_master.csv")
    bo = bo.merge(master[["film_id", "judul", "tahun"]], on="film_id", how="left")
    bo["key"] = bo.judul.map(norm)

    # ---- metrik YouTube hasil scrape
    frames_v, frames_c = [], []
    fmap = {}
    for s in sorted(d.name[3:] for d in BASE.glob("yt_*") if d.is_dir()):
        d = BASE / f"yt_{s}"
        if not (d / "videos.csv").exists():
            continue
        fmap.update(film_map(f"ids_{s}.txt"))
        v = pd.read_csv(d / "videos.csv")
        sc = d / "comments_sentiment.csv"
        c = pd.read_csv(sc if sc.exists() else d / "comments.csv")
        frames_v.append(v); frames_c.append(c)
    v = pd.concat(frames_v, ignore_index=True)
    c = pd.concat(frames_c, ignore_index=True)
    title = dict(zip(v.video_id, v.title))
    lab = lambda vid: short_label(fmap.get(vid) or title.get(vid, ""))  # noqa: E731
    v["film"] = v.video_id.map(lab)
    c["film"] = c.video_id.map(lab)
    if "sent_lexicon" not in c:
        c["sent_lexicon"] = c.text.fillna("").map(lambda t: score(t)[0])

    feat = v.groupby("film").agg(trailers=("video_id", "count"), views_total=("views", "sum"),
                                 likes_total=("likes", "sum")).reset_index()
    cc = c.groupby("film").agg(comments=("comment_id", "count"), unique_commenters=("user", "nunique")).reset_index()
    feat = feat.merge(cc, on="film", how="left")
    for col, name in (("sent_indobert", "indobert"), ("sent_combined", "gabungan"),
                      ("sent_lexicon", "leksikon_emoji"), ("sent_emoji", "emoji")):
        if col not in c:
            continue
        sub = c[c[col].isin(["positif", "netral", "negatif"])]
        g = sub.groupby("film")[col]
        feat = feat.merge((g.apply(lambda s: (s == "positif").mean()) - g.apply(lambda s: (s == "negatif").mean()))
                          .rename(f"net_{name}").round(3).reset_index(), on="film", how="left")
        feat = feat.merge(g.apply(lambda s: (s == "positif").mean()).rename(f"pos_{name}").round(3).reset_index(),
                          on="film", how="left")
    feat["key"] = feat.film.map(norm)

    # ---- tanggal rilis & fitur SEBELUM rilis (butuh timestamp tepat dari API)
    rel = pd.read_csv(BASE / "films.csv")
    rel["key"] = rel.judul.map(norm)
    rel["release"] = pd.to_datetime(rel.tanggal_rilis, errors="coerce", utc=True)
    feat = feat.merge(rel[["key", "release"]], on="key", how="left")
    v["upload"] = pd.to_datetime(v.upload_date.astype(str), format="%Y%m%d", errors="coerce", utc=True)
    v = v.merge(feat[["film", "release"]], on="film", how="left")
    v["upload_after_release"] = v.upload > v.release
    feat = feat.merge(v.groupby("film").upload_after_release.all().rename("semua_trailer_diunggah_setelah_rilis")
                      .reset_index(), on="film", how="left")
    api = load_api_comments(fmap, title)
    pre_note = "tidak tersedia (jalankan ./bit precise dengan YT_API_KEY)"
    if api is not None:
        api = api.merge(feat[["film", "release"]], on="film", how="inner")
        win = api[(api.published < api.release) & (api.published >= api.release - pd.Timedelta(days=60))]
        pre = win.groupby("film").agg(komentar_pra_rilis=("comment_id", "count"),
                                      komentator_pra_rilis=("user", "nunique")).reset_index()
        win = win.assign(lex=win.text.fillna("").map(lambda t: score(t)[0]))
        pre = pre.merge(win.groupby("film").lex.apply(lambda s: round((s == "positif").mean() - (s == "negatif").mean(), 3))
                        .rename("net_sentimen_pra_rilis").reset_index(), on="film", how="left")
        h7 = api[(api.published < api.release - pd.Timedelta(days=7))]
        pre = pre.merge(h7.groupby("film").size().rename("komentar_s.d_H-7").reset_index(), on="film", how="left")
        feat = feat.merge(pre, on="film", how="left")
        api_films = set(api.film)
        for col in ("komentar_pra_rilis", "komentator_pra_rilis", "komentar_s.d_H-7"):
            feat.loc[feat.film.isin(api_films) & feat[col].isna(), col] = 0
        pre_note = f"dari YouTube Data API ({api.api_run.nunique()} run, {len(api):,} komentar), jendela 60 hari sebelum rilis"

    df = feat.merge(bo[["key", "film_id", "penonton", "is_final", "source", "retrieved_at"]], on="key", how="inner")
    missing = sorted(set(feat.film) - set(df.film))
    n = len(df)

    out = BASE / "results" / f"correlation_{datetime.now().strftime('%Y%m%d_%H%M')}"
    out.mkdir(parents=True, exist_ok=True)
    df.drop(columns=["key"]).to_csv(out / "film_features.csv", index=False)

    # ---- Spearman
    metrics = [m for m in ["komentar_pra_rilis", "komentator_pra_rilis", "komentar_s.d_H-7", "net_sentimen_pra_rilis",
                           "views_total", "likes_total", "comments", "unique_commenters",
                           "pos_indobert", "net_indobert", "pos_gabungan", "net_gabungan",
                           "pos_leksikon_emoji", "net_leksikon_emoji", "pos_emoji", "net_emoji"] if m in df]
    rows = []
    for m in metrics:
        ok = df[[m, "penonton"]].dropna()
        if m in ("komentar_pra_rilis", "komentator_pra_rilis", "komentar_s.d_H-7", "net_sentimen_pra_rilis"):
            ok = ok[~df.loc[ok.index, "semua_trailer_diunggah_setelah_rilis"].fillna(False).astype(bool)]
        if len(ok) < 3:
            rows.append({"metrik": m, "n": len(ok), "rho": None, "p_exact": None})
            continue
        r, p = spearman_exact(ok[m], ok.penonton)
        rows.append({"metrik": m, "n": len(ok), "rho": round(r, 3), "p_exact": round(p, 3)})
    sp = pd.DataFrame(rows)
    sp.to_csv(out / "spearman.csv", index=False)

    # ---- audit kolom manual films_master vs hasil scrape
    aud = master[["film_id", "judul", "views_h7", "comments_h7", "sentiment_pos_ratio"]].copy()
    aud["key"] = aud.judul.map(norm)
    aud = aud.merge(feat[["key", "views_total", "comments", "pos_leksikon_emoji"]
                         + (["pos_indobert"] if "pos_indobert" in feat else [])], on="key", how="left")
    aud["views_h7_melebihi_views_sekarang"] = aud.views_h7 > aud.views_total
    aud.drop(columns=["key"]).to_csv(out / "audit_films_master.csv", index=False)
    flagged = aud[aud.views_h7_melebihi_views_sekarang == True]  # noqa: E712

    min_p = round(2 / math.factorial(n), 3) if 2 <= n <= 9 else None
    report = f"""# Korelasi Metrik YouTube vs Penonton Bioskop

_Dibuat {datetime.now().strftime('%d-%m-%Y %H:%M')} WIB · n = {n} film_

## Film yang dianalisis

{df[['film', 'penonton', 'is_final', 'source', 'views_total', 'unique_commenters']].to_markdown(index=False) if n else '-'}

Tidak masuk (tidak ada angka penonton bersumber): {', '.join(missing) or '-'}

## Spearman (p-value eksak, permutasi)

{sp.to_markdown(index=False)}

Fitur pra-rilis: {pre_note}. Film yang semua trailernya diunggah SETELAH rilis dikeluarkan dari fitur pra-rilis.

## ⚠️ Peringatan wajib dibaca

1. **n = {n} terlalu kecil untuk inferensi.** Dengan n = {n}, p-value eksak terkecil yang mungkin adalah {min_p}; hasil apa pun **tidak bisa signifikan pada α = 0,05**. Gunakan hanya sebagai eksplorasi.
2. **Views/likes/komentar total diambil Oktober 2026**, bukan sebelum rilis — ada kebocoran waktu. Untuk prediksi, pakai fitur **pra-rilis** (komentar dengan tanggal tepat dari API). Timestamp yt-dlp ("3 years ago") TIDAK cukup presisi untuk itu.
3. **Penonton belum final** untuk film dengan `is_final = 0`.
4. **Sentimen belum tervalidasi** sampai `./bit sentiment validate` dijalankan dengan anotasi manual.

## Audit `data/films_master.csv`

Kolom `views_h7`, `comments_h7`, `sentiment_pos_ratio`, dll. di `films_master.csv` **tidak punya sumber**. {len(flagged)} film punya `views_h7` (views 7 hari sebelum rilis) **lebih besar** daripada total views trailer saat ini — secara logika mustahil. Angka-angka tersebut, beserta hasil lama `rho = 0,9` dan `LOOCV MAPE` dari `./bit execute`, **tidak boleh dipakai di paper**. Rincian: `audit_films_master.csv`.
"""
    (out / "report.md").write_text(report, encoding="utf-8")
    (out / "run_info.json").write_text(json.dumps({"n": n, "films": df.film.tolist(), "missing": missing,
                                                    "created": datetime.now().isoformat(timespec="seconds")},
                                                   indent=2, ensure_ascii=False))
    print(f"✅ n = {n} film · hasil → {out.relative_to(BASE)}")
    print(sp.to_string(index=False))
    print(f"\nTidak masuk: {', '.join(missing) or '-'}")
    print(f"Audit films_master: {len(flagged)} film views_h7 > views sekarang (angka manual tidak konsisten).")
    if min_p:
        print(f"⚠️  n = {n}: p-value eksak terkecil yang mungkin = {min_p} → tidak bisa signifikan. Eksplorasi saja.")


if __name__ == "__main__":
    main()
