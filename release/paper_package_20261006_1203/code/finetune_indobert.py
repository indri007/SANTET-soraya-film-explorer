#!/usr/bin/env python3
"""
finetune_indobert.py — adaptasi domain model sentimen ke komentar trailer horor Indonesia.

Data   : annotation/annotation_sample.csv (kolom annotator_1, annotator_2, opsional 'adjudikasi')
         Label emas = adjudikasi bila diisi, selain itu label yang disepakati kedua anotator.
Proses : split 80/20 terstratifikasi (seed 42) -> evaluasi model dasar di test
         -> fine-tune pada train -> evaluasi ulang di test yang sama.
Output : models/indobert-horror/            model hasil fine-tune
         results/finetune_<stamp>/          metrics.json, report_base.txt, report_finetuned.txt, test_predictions.csv

Pakai  : python3 finetune_indobert.py [--base MODEL] [--epochs 4] [--lr 2e-5] [--batch 16]
Lalu   : ./bit sentiment predict --model models/indobert-horror
"""
import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
LABELS = ["positif", "netral", "negatif"]
MAP_OUT = {"positive": "positif", "neutral": "netral", "negative": "negatif",
           "label_0": "positif", "label_1": "netral", "label_2": "negatif"}


def gold_labels(path):
    s = pd.read_csv(path)
    for col in ("annotator_1", "annotator_2", "adjudikasi"):
        if col not in s:
            s[col] = ""
        s[col] = s[col].fillna("").astype(str).str.strip().str.lower()
    s["gold"] = np.where(s.adjudikasi.isin(LABELS), s.adjudikasi,
                         np.where((s.annotator_1 == s.annotator_2) & s.annotator_1.isin(LABELS), s.annotator_1, ""))
    g = s[s.gold.isin(LABELS) & s.text.fillna("").str.strip().ne("")]
    return g[["comment_id", "text", "gold"]].reset_index(drop=True)


def predict(model, tok, texts, device, batch=32):
    import torch
    model.eval()
    id2label = {i: MAP_OUT.get(str(l).lower(), str(l).lower()) for i, l in model.config.id2label.items()}
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), batch):
            enc = tok(texts[i:i + batch], truncation=True, max_length=128, padding=True, return_tensors="pt").to(device)
            out += [id2label[int(k)] for k in model(**enc).logits.argmax(-1).cpu()]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="annotation/annotation_sample.csv")
    ap.add_argument("--base", default="w11wo/indonesian-roberta-base-sentiment-classifier")
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--test-size", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-model", default="models/indobert-horror")
    ap.add_argument("--silver", action="store_true",
                    help="latih dengan label konsensus 2 LLM (annotation/llm_labels_all.csv); uji dengan label manusia")
    a = ap.parse_args()

    import torch
    from sklearn.metrics import accuracy_score, classification_report, f1_score
    from sklearn.model_selection import train_test_split
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
    device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

    g = gold_labels(BASE / a.file)
    counts = g.gold.value_counts().to_dict()
    print(f"[*] Label emas (manusia): {len(g)} komentar {counts}")
    if a.silver:
        sf = BASE / "annotation" / "llm_labels_all.csv"
        if not sf.exists():
            sys.exit("⛔ Jalankan dulu: ./bit sentiment llm-annotate --target all")
        S = pd.read_csv(sf)
        cols = [c for c in S if c.startswith("llm_")][:2]
        S = S[(S[cols[0]] == S[cols[1]]) & S[cols[0]].isin(LABELS)].rename(columns={cols[0]: "gold"})
        texts = pd.concat([pd.read_csv(f)[["comment_id", "text"]] for f in sorted(BASE.glob("yt_*/comments.csv"))])
        S = S.merge(texts.drop_duplicates("comment_id"), on="comment_id")[["comment_id", "text", "gold"]]
        if len(g) >= 30:
            tr, te = S[~S.comment_id.isin(g.comment_id)], g
            print(f"[*] Mode perak: latih {len(tr)} label konsensus LLM, uji {len(te)} label MANUSIA")
        else:
            tr, te = train_test_split(S, test_size=a.test_size, stratify=S.gold, random_state=a.seed)
            print("[!] Belum ada label manusia: skor uji hanya mengukur kesesuaian dengan LLM, BUKAN kebenaran.")
    else:
        if len(g) < 100 or min(counts.get(l, 0) for l in LABELS) < 10:
            sys.exit("⛔ Data terlalu sedikit. Minimal 100 komentar berlabel emas dan ≥10 per kelas "
                     "(disarankan 800–1.000). Alternatif: ./bit sentiment finetune --silver")
        tr, te = train_test_split(g, test_size=a.test_size, stratify=g.gold, random_state=a.seed)
    print(f"[*] Train {len(tr)} · Test {len(te)} · device {device}")

    tok = AutoTokenizer.from_pretrained(a.base)
    model = AutoModelForSequenceClassification.from_pretrained(a.base).to(device)
    label2id = {}
    for i, l in model.config.id2label.items():
        label2id[MAP_OUT.get(str(l).lower(), str(l).lower())] = int(i)
    if set(label2id) != set(LABELS):
        sys.exit(f"⛔ Label model dasar tidak dikenali: {model.config.id2label}")

    base_pred = predict(model, tok, te.text.tolist(), device)

    # ---- fine-tune (loop sederhana, tanpa Trainer agar ringan)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    texts, ys = tr.text.tolist(), [label2id[l] for l in tr.gold]
    steps = a.epochs * ((len(texts) + a.batch - 1) // a.batch)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: max(0.0, 1 - s / max(1, steps)))
    model.train()
    for ep in range(a.epochs):
        idx = np.random.permutation(len(texts))
        tot = 0.0
        for i in range(0, len(idx), a.batch):
            b = idx[i:i + a.batch]
            enc = tok([texts[j] for j in b], truncation=True, max_length=128, padding=True,
                      return_tensors="pt").to(device)
            out = model(**enc, labels=torch.tensor([ys[j] for j in b]).to(device))
            out.loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); opt.zero_grad()
            tot += out.loss.item() * len(b)
        print(f"    epoch {ep + 1}/{a.epochs}  loss {tot / len(texts):.4f}")

    ft_pred = predict(model, tok, te.text.tolist(), device)

    def m(pred):
        return {"accuracy": round(accuracy_score(te.gold, pred), 3),
                "f1_macro": round(f1_score(te.gold, pred, labels=LABELS, average="macro"), 3)}

    res = {"base_model": a.base, "mode": "silver(LLM)" if a.silver else "gold(manusia)", "n_gold": len(g), "label_counts": counts, "n_train": len(tr), "n_test": len(te),
           "epochs": a.epochs, "lr": a.lr, "batch": a.batch, "seed": a.seed, "device": device,
           "base_on_test": m(base_pred), "finetuned_on_test": m(ft_pred),
           "created": datetime.now().isoformat(timespec="seconds")}

    mdir = BASE / a.out_model
    mdir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(mdir); tok.save_pretrained(mdir)
    out = BASE / "results" / f"finetune_{datetime.now().strftime('%Y%m%d_%H%M')}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    (out / "report_base.txt").write_text(classification_report(te.gold, base_pred, labels=LABELS, zero_division=0))
    (out / "report_finetuned.txt").write_text(classification_report(te.gold, ft_pred, labels=LABELS, zero_division=0))
    te.assign(pred_base=base_pred, pred_finetuned=ft_pred).to_csv(out / "test_predictions.csv", index=False)

    print(json.dumps({k: res[k] for k in ("n_train", "n_test", "base_on_test", "finetuned_on_test")}, indent=2))
    print(f"\n✅ Model tersimpan: {mdir.relative_to(BASE)}  ·  laporan: {out.relative_to(BASE)}")
    print("Pakai untuk semua komentar: ./bit sentiment predict --model models/indobert-horror")
    print("Catatan: komentar di set test JANGAN dipakai lagi untuk melatih; laporkan skor test ini di paper.")


if __name__ == "__main__":
    main()
