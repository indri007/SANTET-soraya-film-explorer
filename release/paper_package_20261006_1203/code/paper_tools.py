#!/usr/bin/env python3
"""
paper_tools.py — langkah 4, 7, 8, 9, 10 menuju paper (dipanggil lewat ./bit paper).

  rebuild-master : data/films_clean.csv — HANYA angka bersumber (penonton+URL) + hasil scrape/API/Trends.
                   Kolom karangan lama (views_h7, sentiment_pos_ratio, ...) tidak dipakai.
  model          : LOOCV log(penonton) ~ maks. 2 prediktor vs baseline rata-rata. MAPE + bootstrap CI.
  robust         : Spearman + bootstrap CI 95%, koreksi Bonferroni & Benjamini–Hochberg,
                   korelasi parsial (kontrol tahun rilis & waralaba).
  package        : paket reproduksi tanpa teks komentar + SHA-256 + versi pustaka + pernyataan etika.
  status         : checklist 10 langkah + draf bagian Data & Metode berisi angka aktual.
"""
import hashlib
import json
import math
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
RES = BASE / "results"
STAMP = datetime.now().strftime("%Y%m%d_%H%M")
PRE = ["komentar_pra_rilis", "komentator_pra_rilis", "komentar_s.d_H-7", "net_sentimen_pra_rilis", "trends_pra_rilis"]
POST = ["likes_total", "views_total", "comments", "unique_commenters"]


def latest(pattern):
    c = sorted(RES.glob(pattern))
    return c[-1] if c else None


def norm(t):
    t = re.sub(r"\s*\(\d{4}\)\s*$", "", str(t))
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


# ------------------------------------------------------------------ 4. rebuild-master
def rebuild_master():
    cor = latest("correlation_*")
    if not cor:
        sys.exit("Jalankan dulu: ./bit correlate")
    f = pd.read_csv(cor / "film_features.csv")
    master = pd.read_csv(BASE / "data" / "films_master.csv")
    keep = ["film_id", "rumah_produksi", "tahun", "genre", "is_franchise", "momen_rilis"]
    f = f.merge(master[[c for c in keep if c in master]], on="film_id", how="left")
    bo = pd.read_csv(BASE / "data" / "box_office_sources.csv")
    bo = bo[bo.is_official_selected == 1][["film_id", "source_url"]]
    f = f.merge(bo, on="film_id", how="left")
    rel = pd.read_csv(BASE / "films.csv")
    rel["key"] = rel.judul.map(norm)
    f["key"] = f.film.map(norm)
    f = f.merge(rel[["key", "tanggal_rilis"]], on="key", how="left")

    tr = BASE / "data" / "trends" / "trends_daily.csv"
    if tr.exists():
        t = pd.read_csv(tr)
        t = t[(t.property == "web") & t.days_from_release.between(-60, -7)]
        t["key"] = t.film.map(norm)
        f = f.merge(t.groupby("key").score_norm.mean().round(2).rename("trends_pra_rilis").reset_index(),
                    on="key", how="left")
    out = BASE / "data" / "films_clean.csv"
    f.drop(columns=["key"]).to_csv(out, index=False)
    legacy = [c for c in ("views_h7", "likes_h7", "comments_h7", "trends_peak_h7", "sentiment_pos_ratio",
                          "intent_to_watch_ratio", "lead_days") if c in master]
    print(f"✅ {out.relative_to(BASE)}: {len(f)} film, {f.shape[1]} kolom (semua bersumber/terukur)")
    print(f"   Kolom lama TIDAK dipakai (tanpa sumber): {', '.join(legacy)}")
    return f


def load_clean():
    p = BASE / "data" / "films_clean.csv"
    if not p.exists():
        return rebuild_master()
    return pd.read_csv(p)


# ------------------------------------------------------------------ 7. model
def loocv(df, preds):
    y = np.log(df.penonton.values.astype(float))
    X = np.column_stack([np.ones(len(df))] + [df[p].values.astype(float) for p in preds]) if preds else None
    pm, pb = [], []
    for i in range(len(df)):
        tr = np.arange(len(df)) != i
        pb.append(y[tr].mean())
        if preds:
            Xt = X[tr]
            mu, sd = Xt[:, 1:].mean(0), Xt[:, 1:].std(0) + 1e-9
            Xs = np.column_stack([np.ones(tr.sum()), (Xt[:, 1:] - mu) / sd])
            beta = np.linalg.lstsq(Xs, y[tr], rcond=None)[0]
            pm.append(np.r_[1, (X[i, 1:] - mu) / sd] @ beta)
    true = np.exp(y)
    ape_b = np.abs(np.exp(pb) - true) / true
    ape_m = np.abs(np.exp(pm) - true) / true if preds else None
    return ape_m, ape_b


def boot_ci(a, n=5000, seed=42):
    rng = np.random.default_rng(seed)
    m = [rng.choice(a, len(a), replace=True).mean() for _ in range(n)]
    return np.percentile(m, [2.5, 97.5])


def model():
    f = load_clean().dropna(subset=["penonton"])
    pre = [p for p in PRE if p in f and f[p].notna().sum() >= 8]
    if len(pre) >= 1:
        # prediktor ditetapkan apriori: volume komentar pra-rilis (+ Trends bila ada)
        preds = [p for p in ("komentator_pra_rilis", "trends_pra_rilis") if p in pre][:2] or pre[:1]
        mode = "PREDIKTIF (fitur pra-rilis)"
    else:
        preds = [p for p in ("likes_total", "unique_commenters") if p in f][:2]
        mode = "ASOSIATIF (fitur total pasca-rilis — BUKAN prediksi; jalankan ./bit precise)"
    d = f.dropna(subset=preds).copy()
    for p in preds:
        if p not in ("net_sentimen_pra_rilis", "trends_pra_rilis"):
            d[p] = np.log1p(d[p])
    ape_m, ape_b = loocv(d, preds)
    res = {"mode": mode, "n": len(d), "prediktor": preds, "transformasi": "log1p untuk hitungan; target log(penonton)",
           "validasi": "leave-one-out",
           "MAPE_model_%": round(ape_m.mean() * 100, 1), "MAPE_model_CI95_%": [round(x * 100, 1) for x in boot_ci(ape_m)],
           "MAPE_baseline_%": round(ape_b.mean() * 100, 1),
           "MAPE_baseline_CI95_%": [round(x * 100, 1) for x in boot_ci(ape_b)],
           "model_lebih_baik_di_berapa_film": int((ape_m < ape_b).sum())}
    out = RES / f"model_{STAMP}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "model.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    pd.DataFrame({"film": d.film, "penonton": d.penonton, "ape_model": ape_m.round(3), "ape_baseline": ape_b.round(3)}) \
        .to_csv(out / "loocv_per_film.csv", index=False)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    lo, hi = res["MAPE_model_CI95_%"]
    if lo <= res["MAPE_baseline_%"] <= hi:
        print("⚠️  CI MAPE model mencakup MAPE baseline → model belum terbukti lebih baik dari menebak rata-rata.")
    return res


# ------------------------------------------------------------------ 8. robust
def spearman(x, y):
    return pd.Series(x).rank().corr(pd.Series(y).rank())


def partial_spearman(x, y, Z):
    rx, ry = pd.Series(x).rank().values, pd.Series(y).rank().values
    Zr = np.column_stack([np.ones(len(rx))] + [pd.Series(z).rank().values for z in Z.T])
    ex = rx - Zr @ np.linalg.lstsq(Zr, rx, rcond=None)[0]
    ey = ry - Zr @ np.linalg.lstsq(Zr, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


def robust():
    f = load_clean().dropna(subset=["penonton"])
    sp = latest("correlation_*")
    pv = pd.read_csv(sp / "spearman.csv").set_index("metrik")["p_exact"] if sp else pd.Series(dtype=float)
    rng = np.random.default_rng(42)
    rows = []
    metrics = [m for m in PRE + POST + ["pos_indobert", "net_indobert", "pos_leksikon_emoji", "net_leksikon_emoji",
                                        "pos_gabungan", "net_gabungan"] if m in f]
    for m in metrics:
        d = f[[m, "penonton", "tahun", "is_franchise"]].dropna(subset=[m, "penonton"])
        if len(d) < 4:
            continue
        r = spearman(d[m], d.penonton)
        bs = []
        for _ in range(3000):
            idx = rng.integers(0, len(d), len(d))
            b = d.iloc[idx]
            if b[m].nunique() > 1 and b.penonton.nunique() > 1:
                bs.append(spearman(b[m].values, b.penonton.values))
        ctrl = d[["tahun", "is_franchise"]].dropna()
        pr = partial_spearman(d.loc[ctrl.index, m], d.loc[ctrl.index, "penonton"], ctrl.values.astype(float)) \
            if len(ctrl) >= 6 else float("nan")
        rows.append({"metrik": m, "jenis": "pra-rilis" if m in PRE else ("pasca-rilis" if m in POST else "sentimen"),
                     "n": len(d), "rho": round(r, 3),
                     "CI95_bootstrap": f"[{np.percentile(bs, 2.5):.2f}, {np.percentile(bs, 97.5):.2f}]",
                     "p_exact": pv.get(m, np.nan), "rho_parsial_kontrol_tahun_waralaba": round(pr, 3)})
    t = pd.DataFrame(rows)
    k = t.p_exact.notna().sum()
    t["p_bonferroni"] = (t.p_exact * k).clip(upper=1).round(3)
    order = t.p_exact.rank(method="first")
    t["q_BH"] = (t.p_exact * k / order).round(3)
    t = t.sort_values("p_exact")
    t["q_BH"] = t.q_BH[::-1].cummin()[::-1].clip(upper=1)
    out = RES / f"robust_{STAMP}"
    out.mkdir(parents=True, exist_ok=True)
    t.to_csv(out / "robustness.csv", index=False)
    print(t.to_string(index=False))
    sig = t[t.q_BH < 0.05]
    print(f"\nSignifikan setelah koreksi FDR (q < 0,05): {len(sig)} dari {k} uji.")
    return t


# ------------------------------------------------------------------ 9. package
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def package():
    out = BASE / "release" / f"paper_package_{STAMP}"
    (out / "data").mkdir(parents=True, exist_ok=True)
    load_clean().to_csv(out / "data" / "films_clean.csv", index=False)
    frames = []
    for d in sorted(BASE.glob("yt_*")):
        src = d / "comments_sentiment.csv" if (d / "comments_sentiment.csv").exists() else d / "comments.csv"
        if src.exists():
            c = pd.read_csv(src)
            keep = [x for x in ("video_id", "user", "is_reply", "timestamp", "like_count", "sent_indobert",
                                "sent_indobert_score", "sent_lexicon", "sent_emoji", "sent_combined") if x in c]
            frames.append(c[keep].assign(set=d.name[3:]))   # TANPA teks & TANPA comment_id
        v = d / "videos.csv"
        if v.exists():
            shutil.copy(v, out / "data" / f"videos_{d.name[3:]}.csv")
    if frames:
        pd.concat(frames).to_csv(out / "data" / "comments_labels_no_text.csv", index=False)
    for pat in ("ids_*.txt", "films.csv", "data/box_office_sources.csv", "*.py", "bit"):
        for p in BASE.glob(pat):
            (out / "code" / p.parent.relative_to(BASE)).mkdir(parents=True, exist_ok=True)
            shutil.copy(p, out / "code" / p.relative_to(BASE))
    for pat in ("correlation_*", "robust_*", "model_*", "analysis_*", "sentiment_*"):
        lt = latest(pat)
        if lt:
            shutil.copytree(lt, out / "results" / lt.name, ignore=shutil.ignore_patterns("*.graphml"))
    ann = BASE / "annotation" / "validation_result.json"
    if ann.exists():
        shutil.copy(ann, out / "results" / "validation_result.json")
    vers = {}
    for mod in ("pandas", "numpy", "networkx", "matplotlib", "torch", "transformers", "sklearn", "yt_dlp"):
        try:
            m = __import__(mod)
            vers[mod] = getattr(m, "__version__", getattr(getattr(m, "version", None), "__version__", "?"))
        except Exception:  # noqa: BLE001
            pass
    vers["python"] = sys.version.split()[0]
    (out / "ENVIRONMENT.json").write_text(json.dumps(vers, indent=2))
    (out / "README_DATA.md").write_text(f"""# Paket Data & Kode — Riset Komentar Trailer Film Indonesia

Dibuat {datetime.now().strftime('%d-%m-%Y %H:%M')} WIB.

## Isi
- `data/films_clean.csv` — metrik per film; penonton hanya dari sumber ber-URL (`code/data/box_office_sources.csv`).
- `data/comments_labels_no_text.csv` — label & metadata komentar **tanpa teks dan tanpa ID komentar**.
- `data/videos_*.csv` — metadata trailer publik.
- `results/` — hasil analisis, korelasi, uji ketahanan, model, validasi.
- `code/` — seluruh skrip pipeline (`bit`), daftar ID video, tanggal rilis.

## Etika
Data berasal dari komentar publik YouTube. Identitas komentator dipseudonimkan dengan HMAC-SHA256
dan kunci rahasia yang tidak dipublikasikan. Teks komentar dan ID komentar tidak dibagikan untuk
mencegah identifikasi ulang; peneliti dapat mengumpulkan ulang data dengan daftar ID video dan skrip di `code/`.

## Integritas
Checksum SHA-256 seluruh berkas ada di `MANIFEST.sha256`.
""", encoding="utf-8")
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "MANIFEST.sha256")
    (out / "MANIFEST.sha256").write_text("".join(f"{sha256(p)}  {p.relative_to(out)}\n" for p in files))
    print(f"✅ {out.relative_to(BASE)}: {len(files)} berkas + MANIFEST.sha256")
    print("   Unggah (bila sudah siap & disetujui): hf upload 1ndrikartika007/<nama-dataset> "
          f"{out.relative_to(BASE)} . --repo-type dataset --private")


# ------------------------------------------------------------------ 10. status
def status(log):
    f = load_clean()
    steps = json.loads(log) if log else {}
    lines = [f"# Status Pipeline Paper — {datetime.now().strftime('%d-%m-%Y %H:%M')} WIB", "",
             "| Langkah | Status | Keterangan |", "|---|---|---|"]
    for k, (st, note) in sorted(steps.items(), key=lambda kv: int(kv[0].split(".")[0])):
        lines.append(f"| {k} | {st} | {note} |")
    n_comments = sum(len(pd.read_csv(p)) for p in BASE.glob("yt_*/comments.csv"))
    n_videos = sum(len(pd.read_csv(p)) for p in BASE.glob("yt_*/videos.csv"))
    houses = ", ".join(sorted(f.rumah_produksi.dropna().unique())) if "rumah_produksi" in f else "-"
    mdl = latest("model_*")
    mres = json.loads((mdl / "model.json").read_text()) if mdl else {}
    val = BASE / "annotation" / "validation_result.json"
    vres = json.loads(val.read_text()) if val.exists() else {}
    lines += ["", "## Draf bagian Data & Metode (angka terisi otomatis — periksa sebelum dipakai)", "",
              f"Data dikumpulkan dari {n_videos} trailer dan teaser resmi pada kanal YouTube rumah produksi, "
              f"mencakup {f.film.nunique()} film ({houses}). Sebanyak {n_comments:,} komentar diambil menggunakan "
              "yt-dlp dengan batas 500 komentar per video, urutan terbaru"
              + ("; komentar dengan tanggal publikasi tepat diambil ulang melalui YouTube Data API v3"
                 if any((BASE / "data" / "youtube_api").glob("*/comments.csv")) else "") + ". "
              "Identitas komentator dipseudonimkan dengan HMAC-SHA256. Jumlah penonton bioskop diambil dari "
              f"sumber publik ber-URL; {int(f.penonton.notna().sum())} film memiliki angka penonton terverifikasi.",
              "",
              "Sentimen komentar diklasifikasikan dengan model RoBERTa bahasa Indonesia yang di-fine-tune pada SmSA "
              "(w11wo/indonesian-roberta-base-sentiment-classifier), leksikon domain dengan polaritas emoji, "
              "dan dua LLM lokal (qwen3:8b, gemma2:9b) sebagai anotator pembanding"
              + (f"; keandalan dievaluasi terhadap anotasi manual ({vres.get('sumber_label_emas', '')})."
                 if vres and not str(vres.get('sumber_label_emas', '')).startswith('belum') else
                 ". [BELUM DIVALIDASI dengan anotasi manual — jangan klaim akurasi sentimen.]")
              + " Hubungan metrik dengan penonton diuji dengan korelasi Spearman (uji permutasi eksak), "
              "bootstrap CI 95%, koreksi Benjamini–Hochberg, dan korelasi parsial dengan kontrol tahun rilis dan waralaba.",
              "",
              (f"Model {mres.get('mode', '')} dengan prediktor {', '.join(mres.get('prediktor', []))} dievaluasi "
               f"secara leave-one-out (n = {mres.get('n')}): MAPE {mres.get('MAPE_model_%')}% "
               f"(CI95 {mres.get('MAPE_model_CI95_%')}) dibanding baseline rata-rata {mres.get('MAPE_baseline_%')}%."
               + (" Model TIDAK lebih baik dari baseline." if mres and mres.get('MAPE_model_%', 0) >= mres.get('MAPE_baseline_%', 0)
                  else " Perbedaan perlu dibaca bersama CI.")
               if mres else "Model belum dijalankan.")]
    out = RES / "paper_status.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:4 + len(steps)]))
    print(f"\n📄 {out.relative_to(BASE)}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"rebuild-master": rebuild_master, "model": model, "robust": robust, "package": package}.get(
        cmd, lambda: status(sys.argv[2] if len(sys.argv) > 2 else ""))()
