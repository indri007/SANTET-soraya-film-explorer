#!/usr/bin/python3
"""
trends_collect.py — Kumpulkan Google Trends per film (Indonesia).

Contoh:
  python trends_collect.py --films films.csv --out data/trends --anchor "film horor"

Output (CSV, bisa resume):
  trends_daily.csv    -> skor harian H-90..H+60 per film, Web & YouTube Search
  trends_region.csv   -> skor per provinsi
  trends_related.csv  -> related queries (top & rising)
  trends_long.csv     -> mingguan 2020–sekarang (2 jendela, ≤ 5 tahun agar tetap mingguan)

Normalisasi: setiap query berisi [judul, anchor]. Kolom score_norm = score / rata2(anchor)
sehingga skor antar film bisa dibandingkan.
"""
import argparse
import json
import os
import random
import time
from datetime import date, datetime, timedelta, timezone

try:
    import pandas as pd
    from pytrends.request import TrendReq
except ImportError:
    pass

PROPS = {"web": "", "youtube": "youtube"}


def now():
    return datetime.now(timezone.utc).isoformat()


def polite_sleep(base):
    time.sleep(base + random.uniform(0, base))


def with_retry(fn, base_sleep):
    for attempt in range(6):
        try:
            return fn()
        except Exception as e:  # pytrends melempar ResponseError 429
            wait = base_sleep * (2 ** attempt)
            print(f"   ! {type(e).__name__}: {str(e)[:80]} — tunggu {wait:.0f}s")
            time.sleep(wait)
    return None


def append(df, path):
    if df is None or df.empty:
        return
    df.to_csv(path, mode="a", header=not os.path.exists(path), index=False, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--films", default="films.csv")
    ap.add_argument("--out", default="data/trends")
    ap.add_argument("--anchor", default="film horor")
    ap.add_argument("--geo", default="ID")
    ap.add_argument("--before", type=int, default=90)
    ap.add_argument("--after", type=int, default=60)
    ap.add_argument("--sleep", type=float, default=8.0, help="jeda dasar antar request (detik)")
    ap.add_argument("--repeat", type=int, default=1, help="ambil ulang N kali (sampel Trends berubah)")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    prog_path = os.path.join(args.out, "progress.json")
    done = set(json.load(open(prog_path))) if os.path.exists(prog_path) else set()
    films = pd.read_csv(args.films)
    py = TrendReq(hl="id-ID", tz=-420, timeout=(10, 30), retries=0)

    for _, film in films.iterrows():
        kw = str(film["keyword_trends"]).strip()
        rel = date.fromisoformat(str(film["tanggal_rilis"]))
        start = rel - timedelta(days=args.before)
        end = min(rel + timedelta(days=args.after), date.today())
        tf = f"{start} {end}"

        for rep in range(args.repeat):
            for prop_name, gprop in PROPS.items():
                job = f"{kw}|{prop_name}|{rep}"
                if job in done:
                    continue
                print(f"{kw} [{prop_name}] {tf} (ulang {rep + 1})")

                def daily():
                    py.build_payload([kw, args.anchor], timeframe=tf, geo=args.geo, gprop=gprop)
                    return py.interest_over_time()

                df = with_retry(daily, args.sleep)
                if df is not None and not df.empty:
                    anchor_mean = df[args.anchor].mean() or 1
                    out = pd.DataFrame({
                        "film": film["judul"], "keyword": kw, "property": prop_name,
                        "date": df.index.date, "days_from_release": [(d - rel).days for d in df.index.date],
                        "score": df[kw].values, "anchor": args.anchor,
                        "anchor_score": df[args.anchor].values,
                        "score_norm": (df[kw] / anchor_mean * 100).round(2).values,
                        "is_partial": df.get("isPartial", False), "repeat": rep,
                        "retrieved_at": now()})
                    append(out, os.path.join(args.out, "trends_daily.csv"))

                if prop_name == "web" and rep == 0:
                    reg = with_retry(lambda: py.interest_by_region(resolution="REGION",
                                                                   inc_low_vol=True), args.sleep)
                    if reg is not None and not reg.empty:
                        reg = reg.reset_index().rename(columns={"geoName": "region", kw: "score"})
                        reg = reg[["region", "score"]].assign(film=film["judul"], keyword=kw,
                                                              timeframe=tf, retrieved_at=now())
                        append(reg, os.path.join(args.out, "trends_region.csv"))

                    rq = with_retry(py.related_queries, args.sleep) or {}
                    rows = []
                    for kind in ("top", "rising"):
                        t = (rq.get(kw) or {}).get(kind)
                        if t is not None:
                            rows.append(t.assign(kind=kind))
                    if rows:
                        append(pd.concat(rows).assign(film=film["judul"], keyword=kw, retrieved_at=now()),
                               os.path.join(args.out, "trends_related.csv"))

                done.add(job)
                json.dump(sorted(done), open(prog_path, "w"))
                polite_sleep(args.sleep)

        # Tren jangka panjang (mingguan) — dua jendela ≤ 5 tahun.
        for win in ("2020-01-01 2024-12-31", f"2022-01-01 {date.today()}"):
            job = f"{kw}|long|{win}"
            if job in done:
                continue

            def long():
                py.build_payload([kw, args.anchor], timeframe=win, geo=args.geo)
                return py.interest_over_time()

            df = with_retry(long, args.sleep)
            if df is not None and not df.empty:
                append(pd.DataFrame({"film": film["judul"], "keyword": kw, "window": win,
                                     "week": df.index.date, "score": df[kw].values,
                                     "anchor_score": df[args.anchor].values, "retrieved_at": now()}),
                       os.path.join(args.out, "trends_long.csv"))
            done.add(job)
            json.dump(sorted(done), open(prog_path, "w"))
            polite_sleep(args.sleep)

    print("Selesai.")


if __name__ == "__main__":
    main()
