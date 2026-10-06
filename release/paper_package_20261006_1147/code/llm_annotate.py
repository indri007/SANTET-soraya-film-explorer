#!/usr/bin/env python3
"""
llm_annotate.py — anotator sentimen berbasis LLM lokal (Ollama), sebagai PELENGKAP anotator manusia.

  --target sample  : labeli annotation/annotation_sample.csv  -> annotation/llm_labels.csv
                     (dipakai ./bit sentiment validate untuk kappa manusia–LLM dan akurasi LLM)
  --target all     : labeli semua komentar -> annotation/llm_labels_all.csv
                     (label "perak" untuk ./bit sentiment finetune --silver)

Model default: qwen3:8b dan gemma2:9b (dua model berbeda keluarga = dua "anotator" independen).
Suhu 0, prompt tetap, output satu kata. Hasil LLM BUKAN pengganti validasi manusia:
minimal 100–150 komentar tetap harus dilabeli manusia untuk mengukur keandalan LLM.
"""
import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
URL = "http://localhost:11434/api/chat"
LABELS = ["positif", "netral", "negatif"]

SYSTEM = """Kamu anotator sentimen untuk komentar YouTube pada trailer film Indonesia (kebanyakan horor).
Nilai SIKAP PENULIS TERHADAP FILM/TRAILER, bukan topiknya.
- positif: memuji, antusias, ingin menonton, kagum. Untuk film horor, "serem", "ngeri", "merinding",
  "takut banget", "gila", "parah" biasanya PUJIAN -> positif. "ga sabar" = antusias -> positif.
- negatif: kritik, kecewa, mengejek film, bosan, menolak menonton, membandingkan buruk dengan versi lama.
- netral: pertanyaan, info, tag teman, di luar topik, atau campuran seimbang.
Emoji: 😂🤣 bisa tawa senang atau ejekan; 😭😢 sering berarti terharu/ga sabar. Baca konteks.
Jawab HANYA satu kata: positif, netral, atau negatif."""


def ask(model, text, retries=3):
    body = {"model": model, "stream": False, "think": False,
            "options": {"temperature": 0, "num_predict": 8, "seed": 42},
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": f"Komentar: {str(text)[:1200]}\nLabel:"}]}
    for i in range(retries):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.loads(r.read())["message"]["content"].lower()
            out = re.sub(r"<think>.*?</think>", "", out, flags=re.S)
            m = re.search(r"positif|netral|negatif|positive|neutral|negative", out)
            if m:
                return {"positive": "positif", "neutral": "netral", "negative": "negatif"}.get(m.group(), m.group())
            return "netral"
        except Exception as e:  # noqa: BLE001
            if i == retries - 1:
                print(f"\n[!] {model} gagal: {e}")
                return ""
            time.sleep(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["qwen3:8b", "gemma2:9b"])
    ap.add_argument("--target", choices=["sample", "all"], default="sample")
    ap.add_argument("--limit", type=int, default=0, help="untuk uji coba")
    a = ap.parse_args()

    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
    except Exception:
        sys.exit("⛔ Ollama tidak berjalan. Buka aplikasi Ollama atau jalankan: ollama serve")

    if a.target == "sample":
        src = BASE / "annotation" / "annotation_sample.csv"
        out = BASE / "annotation" / "llm_labels.csv"
        df = pd.read_csv(src)[["comment_id", "text"]]
    else:
        frames = [pd.read_csv(f)[["comment_id", "text"]] for f in sorted(BASE.glob("yt_*/comments.csv"))]
        df = pd.concat(frames).drop_duplicates("comment_id")
        out = BASE / "annotation" / "llm_labels_all.csv"
    if a.limit:
        df = df.head(a.limit)

    done = pd.read_csv(out) if out.exists() else pd.DataFrame({"comment_id": []})
    df = df.merge(done, on="comment_id", how="left") if len(done) else df
    for m in a.models:
        col = "llm_" + re.sub(r"[^a-z0-9]+", "_", m.lower()).strip("_")
        if col not in df:
            df[col] = ""
        todo = df[col].fillna("").eq("")
        print(f"[*] {m}: {int(todo.sum()):,} komentar")
        t0 = time.time()
        for k, i in enumerate(df.index[todo], 1):
            df.at[i, col] = ask(m, df.at[i, "text"])
            if k % 25 == 0 or k == int(todo.sum()):
                rate = k / (time.time() - t0)
                print(f"    {k:,}/{int(todo.sum()):,}  ({rate:.1f}/detik)", end="\r")
                df.drop(columns=["text"]).to_csv(out, index=False)   # simpan berkala, bisa dilanjutkan
        print()
        print("    distribusi:", df[col].value_counts().to_dict())
    df.drop(columns=["text"]).to_csv(out, index=False)
    cols = [c for c in df if c.startswith("llm_")]
    if len(cols) >= 2:
        agree = (df[cols[0]] == df[cols[1]]).mean()
        print(f"✅ {out.relative_to(BASE)} · kesepakatan {cols[0]} vs {cols[1]}: {agree:.1%}")
    else:
        print(f"✅ {out.relative_to(BASE)}")


if __name__ == "__main__":
    main()
