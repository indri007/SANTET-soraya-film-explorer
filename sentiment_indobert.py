#!/usr/bin/env python3
"""
sentiment_indobert.py — sentimen komentar dengan model transformer bahasa Indonesia
+ alur validasi manual (sampel anotasi, Cohen's kappa, akurasi/F1).

Subperintah
  predict   [--sets soraya ivanna] [--model ID] [--batch 32]
            -> yt_<set>/comments_sentiment.csv  (label, skor keyakinan, label leksikon)
            -> results/sentiment_<stamp>/sentiment_film_indobert.csv + perbandingan dengan leksikon
  sample    [--n 300] [--seed 42]
            -> annotation/annotation_sample.csv  (kolom annotator_1, annotator_2 kosong)
  validate  [--file annotation/annotation_sample.csv]
            -> Cohen's kappa antar-anotator, lalu akurasi & F1-macro IndoBERT vs leksikon terhadap label emas

Label anotasi yang dipakai: positif / netral / negatif
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from emoji_sentiment import emoji_label, has_letters  # noqa: E402
DEFAULT_MODEL = "w11wo/indonesian-roberta-base-sentiment-classifier"
ALT_MODEL = "mdhugol/indonesia-bert-sentiment-classification"
# mdhugol memakai LABEL_0/1/2 = positive/neutral/negative (sesuai model card)
LABEL_MAP = {"positive": "positif", "neutral": "netral", "negative": "negatif",
             "label_0": "positif", "label_1": "netral", "label_2": "negatif"}
LABELS = ["positif", "netral", "negatif"]


def load_comments(sets):
    frames = []
    for s in sets:
        f = BASE / f"yt_{s}" / "comments.csv"
        if f.exists():
            c = pd.read_csv(f)
            c["set"] = s
            frames.append(c)
        else:
            print(f"[!] {f} tidak ada — jalankan dulu: ./bit scrape {s}")
    if not frames:
        sys.exit("Tidak ada komentar.")
    return pd.concat(frames, ignore_index=True)


def lexicon_labels(texts):
    sys.path.insert(0, str(BASE))
    from analyze_youtube import score
    return [score(t)[0] for t in texts]


# ------------------------------------------------------------------ predict
def cmd_predict(a):
    try:
        import torch
        from transformers import pipeline
    except ImportError:
        sys.exit("⛔ Paket belum ada. Jalankan: ./bit install-nlp")

    device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Model  : {a.model}\n[*] Device : {device}")
    clf = pipeline("text-classification", model=a.model, revision=a.revision, device=device,
                   truncation=True, max_length=256)
    model_sha = getattr(clf.model.config, "_commit_hash", None)

    c = load_comments(a.sets)
    texts = c["text"].fillna("").astype(str).str.slice(0, 2000).tolist()
    print(f"[*] Memproses {len(texts):,} komentar ...")
    preds = []
    for i in range(0, len(texts), a.batch):
        out = clf([t if t.strip() else "." for t in texts[i:i + a.batch]], batch_size=a.batch)
        preds += out
        print(f"    {min(i + a.batch, len(texts)):,}/{len(texts):,}", end="\r")
    print()
    c["sent_indobert"] = [LABEL_MAP.get(p["label"].lower(), p["label"].lower()) for p in preds]
    c["sent_indobert_score"] = [round(p["score"], 4) for p in preds]
    c.loc[c["text"].fillna("").str.strip() == "", ["sent_indobert", "sent_indobert_score"]] = ["netral", 0.0]
    c["sent_lexicon"] = lexicon_labels(c["text"].fillna(""))   # kata + emoji
    c["sent_emoji"] = c["text"].fillna("").map(emoji_label)
    # Gabungan: IndoBERT, kecuali (a) komentar hanya emoji tanpa kata, atau
    # (b) keyakinan IndoBERT < 0,6 dan emoji memberi polaritas jelas -> pakai label emoji.
    only_emoji = ~c["text"].fillna("").map(has_letters) & c.sent_emoji.isin(LABELS)
    weak = (c.sent_indobert_score < 0.6) & c.sent_emoji.isin(["positif", "negatif"])
    c["sent_combined"] = c.sent_indobert.where(~(only_emoji | weak), c.sent_emoji)
    c["combined_rule"] = "indobert"
    c.loc[weak, "combined_rule"] = "emoji_keyakinan_rendah"
    c.loc[only_emoji, "combined_rule"] = "emoji_saja"

    for s, grp in c.groupby("set"):
        grp.drop(columns=["set"]).to_csv(BASE / f"yt_{s}" / "comments_sentiment.csv", index=False)

    # agregat per film (pakai label film dari analyze_youtube)
    sys.path.insert(0, str(BASE))
    from analyze_youtube import film_map, short_label
    fmap = {}
    for s in a.sets:
        fmap.update(film_map(f"ids_{s}.txt"))
    vids = pd.concat([pd.read_csv(BASE / f"yt_{s}" / "videos.csv") for s in a.sets
                      if (BASE / f"yt_{s}" / "videos.csv").exists()])
    title = dict(zip(vids.video_id, vids.title))
    c["film"] = c.video_id.map(lambda v: short_label(fmap.get(v) or title.get(v, "")))

    def share(col):
        return c.groupby("film")[col].value_counts(normalize=True).unstack(fill_value=0) \
            .reindex(columns=LABELS, fill_value=0).round(3)

    ib, lx, cb = share("sent_indobert"), share("sent_lexicon"), share("sent_combined")
    agg = ib.add_prefix("indobert_").join(cb.add_prefix("gabungan_")).join(lx.add_prefix("lexicon_"))
    em = c[c.sent_emoji != "tanpa_emoji"].groupby("film").sent_emoji.value_counts(normalize=True) \
        .unstack(fill_value=0).reindex(columns=LABELS, fill_value=0).round(3).add_prefix("emoji_")
    agg = agg.join(em)
    agg["pct_beremoji"] = (c.sent_emoji != "tanpa_emoji").groupby(c["film"]).mean().round(3)
    agg.insert(0, "n", c.groupby("film").size())
    agg["agreement_indobert_vs_lexicon"] = (c.sent_indobert == c.sent_lexicon) \
        .groupby(c["film"]).mean().round(3)
    agg = agg.sort_values("indobert_positif", ascending=False)

    out = BASE / "results" / f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M')}"
    out.mkdir(parents=True, exist_ok=True)
    agg.to_csv(out / "sentiment_film_indobert.csv")
    pd.crosstab(c.sent_lexicon, c.sent_indobert, margins=True).to_csv(out / "crosstab_lexicon_vs_indobert.csv")
    low = c[c.sent_indobert_score < 0.6]
    (out / "run_info.json").write_text(json.dumps({
        "model": a.model, "model_revision": model_sha or a.revision, "device": device,
        "n_comments": len(c), "sets": a.sets, "max_length": 256,
        "low_confidence_share(<0.6)": round(len(low) / len(c), 3),
        "overall_agreement_with_lexicon": round((c.sent_indobert == c.sent_lexicon).mean(), 3),
        "combined_rule_counts": c.combined_rule.value_counts().to_dict(),
        "created": datetime.now().isoformat(timespec="seconds"),
    }, indent=2))

    print(f"\n✅ Selesai → {out.relative_to(BASE)}")
    print(agg[["n", "indobert_positif", "indobert_negatif", "gabungan_positif", "gabungan_negatif",
               "lexicon_positif", "lexicon_negatif", "pct_beremoji"]].to_string())
    print("\nAturan gabungan:", c.combined_rule.value_counts().to_dict())
    print(f"\nKesesuaian IndoBERT vs leksikon: {(c.sent_indobert == c.sent_lexicon).mean():.1%} · "
          f"keyakinan rendah (<0,6): {len(low) / len(c):.1%}")
    print("Langkah berikut: ./bit sentiment sample  →  isi anotasi  →  ./bit sentiment validate")


# ------------------------------------------------------------------ sample
def cmd_sample(a):
    frames = []
    for s in sorted(d.name[3:] for d in BASE.glob("yt_*") if d.is_dir()):
        f = BASE / f"yt_{s}" / "comments_sentiment.csv"
        if f.exists():
            frames.append(pd.read_csv(f))
    if not frames:
        sys.exit("Jalankan dulu: ./bit sentiment predict")
    c = pd.concat(frames, ignore_index=True)
    c = c[c["text"].fillna("").str.strip().str.len() >= 3]
    # stratifikasi per label IndoBERT agar kelas minoritas (negatif) tetap terwakili
    per = max(1, a.n // 3)
    smp = pd.concat([g.sample(min(len(g), per), random_state=a.seed)
                     for _, g in c.groupby("sent_indobert")])
    if len(smp) < a.n:
        rest = c.drop(smp.index)
        smp = pd.concat([smp, rest.sample(min(len(rest), a.n - len(smp)), random_state=a.seed)])
    smp = smp.sample(frac=1, random_state=a.seed)  # acak urutan
    sheet = smp[["comment_id", "video_id", "text"]].copy()
    sheet["annotator_1"] = ""
    sheet["annotator_2"] = ""
    sheet["catatan"] = ""
    hidden = smp[["comment_id", "sent_indobert", "sent_indobert_score", "sent_lexicon", "sent_emoji", "sent_combined"]]
    d = BASE / "annotation"
    d.mkdir(exist_ok=True)
    old = d / "annotation_sample.csv"
    if old.exists() and not a.force:
        o = pd.read_csv(old)
        filled = sum(o[col].fillna("").astype(str).str.strip().ne("").sum()
                     for col in ("annotator_1", "annotator_2") if col in o)
        if filled:
            sys.exit(f"⛔ annotation_sample.csv sudah berisi {filled} label. Tidak ditimpa. "
                     "Pakai --force bila memang ingin membuat ulang (buat cadangan dulu).")
    sheet.to_csv(d / "annotation_sample.csv", index=False)
    hidden.to_csv(d / "_model_labels_hidden.csv", index=False)
    (d / "PANDUAN_ANOTASI.md").write_text(GUIDE, encoding="utf-8")
    print(f"✅ {len(sheet)} komentar → annotation/annotation_sample.csv")
    print("   Label model disimpan terpisah (_model_labels_hidden.csv) supaya anotator tidak terpengaruh.")
    print("   Baca annotation/PANDUAN_ANOTASI.md, isi kolom annotator_1 & annotator_2 secara terpisah,")
    print("   lalu jalankan: ./bit sentiment validate")


GUIDE = """# Panduan Anotasi Sentimen Komentar Trailer

Isi kolom `annotator_1` (anotator pertama) dan `annotator_2` (anotator kedua) dengan salah satu:
`positif`, `netral`, `negatif`. Kedua anotator bekerja **terpisah** dan tidak saling melihat jawaban.

| Label | Kapan dipakai | Contoh |
|---|---|---|
| positif | Pujian, antusias, ingin menonton, kagum — termasuk "serem banget" sebagai pujian film horor | "gila merinding, wajib nonton", "Luna Maya cantik banget" |
| negatif | Kritik, kecewa, mengejek, menolak menonton | "trailernya spoiler semua", "males, ceritanya itu-itu aja" |
| netral | Pertanyaan, info, tag teman, komentar di luar topik, campuran seimbang | "tayang tanggal berapa?", "@teman ayo", "first" |

Aturan tambahan:
1. Nilai **sikap terhadap film/trailer**, bukan topik. "Takut banget" pada film horor = positif bila nadanya kagum.
2. Sarkasme: labeli sesuai maksud sebenarnya.
   Emoji ikut dibaca: 😂🤣 bisa tawa senang atau mengejek; 😭😢 sering berarti terharu/ga sabar, bukan sedih.
3. Ragu di antara dua label → pilih `netral` dan tulis alasannya di kolom `catatan`.
4. Jangan membuka `_model_labels_hidden.csv` sebelum anotasi selesai.
"""


# ------------------------------------------------------------------ validate
def kappa(a, b):
    from sklearn.metrics import cohen_kappa_score
    return cohen_kappa_score(a, b, labels=LABELS)


def cmd_validate(a):
    from sklearn.metrics import accuracy_score, classification_report, cohen_kappa_score, f1_score
    d = BASE / "annotation"
    s = pd.read_csv(BASE / a.file)
    for col in ("annotator_1", "annotator_2", "adjudikasi"):
        if col not in s:
            s[col] = ""
        s[col] = s[col].fillna("").astype(str).str.strip().str.lower()
    s = s.merge(pd.read_csv(d / "_model_labels_hidden.csv"), on="comment_id", how="left")
    llm_file = d / "llm_labels.csv"
    llm_cols = []
    if llm_file.exists():
        L = pd.read_csv(llm_file)
        llm_cols = [c for c in L if c.startswith("llm_")]
        s = s.merge(L, on="comment_id", how="left")
        if len(llm_cols) >= 2:
            s["llm_konsensus"] = s[llm_cols[0]].where(s[llm_cols[0]] == s[llm_cols[1]], "")
            llm_cols.append("llm_konsensus")

    def kap(x, y):
        m = x.isin(LABELS) & y.isin(LABELS)
        return (round(cohen_kappa_score(x[m], y[m], labels=LABELS), 3), int(m.sum())) if m.sum() >= 10 else (None, int(m.sum()))

    def interp(x):
        if x is None:
            return "-"
        return ("hampir sempurna" if x > .8 else "substansial" if x > .6 else "sedang" if x > .4
                else "cukup" if x > .2 else "lemah")

    res = {}
    h1, h2 = s.annotator_1.isin(LABELS), s.annotator_2.isin(LABELS)
    if (h1 & h2).sum() >= 30:
        k, n = kap(s.annotator_1, s.annotator_2)
        res["kappa_manusia_1_vs_2"] = {"kappa": k, "n": n, "tafsiran": interp(k)}
        s["gold"] = s.adjudikasi.where(s.adjudikasi.isin(LABELS),
                                       s.annotator_1.where(s.annotator_1 == s.annotator_2, ""))
        res["sumber_label_emas"] = "2 anotator manusia (sepakat) + adjudikasi bila ada"
    elif h1.sum() >= 30:
        s["gold"] = s.adjudikasi.where(s.adjudikasi.isin(LABELS), s.annotator_1.where(h1, ""))
        res["sumber_label_emas"] = "1 anotator manusia (annotator_1) — tambahkan annotator_2 untuk kappa antar-manusia"
    else:
        s["gold"] = ""
        res["sumber_label_emas"] = f"belum ada (annotator_1 terisi {int(h1.sum())} baris; butuh >=30)"

    for c in llm_cols:
        if c == "llm_konsensus":
            continue
        if s.gold.isin(LABELS).sum() >= 10:
            k, n = kap(s.gold, s[c])
            res[f"kappa_manusia_vs_{c}"] = {"kappa": k, "n": n, "tafsiran": interp(k)}
    if len(llm_cols) >= 3:
        k, n = kap(s[llm_cols[0]], s[llm_cols[1]])
        res[f"kappa_{llm_cols[0]}_vs_{llm_cols[1]}"] = {"kappa": k, "n": n, "tafsiran": interp(k)}

    g = s[s.gold.isin(LABELS)]
    methods = {"indobert": "sent_indobert", "leksikon+emoji": "sent_lexicon", "indobert+emoji": "sent_combined",
               **{c: c for c in llm_cols}}
    if len(g) >= 30:
        perf = {}
        for name, col in methods.items():
            if col not in g:
                continue
            gg = g[g[col].isin(LABELS)]
            if len(gg) < 10:
                continue
            perf[name] = {"n": len(gg), "accuracy": round(accuracy_score(gg.gold, gg[col]), 3),
                          "f1_macro": round(f1_score(gg.gold, gg[col], labels=LABELS, average="macro"), 3)}
        res["kinerja_vs_label_emas"] = dict(sorted(perf.items(), key=lambda kv: -kv[1]["f1_macro"]))
        best = max(perf, key=lambda k: perf[k]["f1_macro"])
        rep = classification_report(g.gold, g[methods[best]].where(g[methods[best]].isin(LABELS), "netral"),
                                    labels=LABELS, zero_division=0)
        (d / "validation_report_best.txt").write_text(f"Metode terbaik: {best}\n\n{rep}")
    elif llm_cols:
        res["kesepakatan_llm_vs_indobert"] = {c: round((s[c] == s.sent_indobert).mean(), 3)
                                              for c in llm_cols if c != "llm_konsensus"}

    (d / "validation_result.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    print(json.dumps(res, indent=2, ensure_ascii=False))
    print("\nPanduan: kappa >= 0,61 dan F1-macro >= 0,70 umumnya cukup untuk dilaporkan di jurnal.")
    if not g.shape[0]:
        print("Belum ada label manusia. Isi minimal kolom annotator_1 (100–150 baris) untuk mengukur keandalan LLM.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("predict")
    p.add_argument("--sets", nargs="+", default=sorted(d.name[3:] for d in BASE.glob("yt_*") if d.is_dir()))
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--revision", default=None)
    p.add_argument("--batch", type=int, default=32)
    s = sub.add_parser("sample")
    s.add_argument("--n", type=int, default=300)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("--force", action="store_true")
    v = sub.add_parser("validate")
    v.add_argument("--file", default="annotation/annotation_sample.csv")
    a = ap.parse_args()
    {"predict": cmd_predict, "sample": cmd_sample, "validate": cmd_validate}[a.cmd](a)


if __name__ == "__main__":
    main()
