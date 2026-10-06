#!/usr/bin/env python3
"""
analyze_youtube.py — analisis lengkap hasil yt-dlp untuk riset film Soraya.

Input  : yt_<set>/videos.csv, comments.csv, edges.csv  (+ ids_<set>.txt untuk label film)
Output : results/analysis_<YYYYMMDD_HHMM>/
           video_metrics.csv     metrik per trailer + sentralitas jaringan + komunitas
           film_metrics.csv      agregat per film
           film_overlap.csv      irisan komentator antarfilm (jumlah & Jaccard)
           timeline_monthly.csv  jumlah komentar per bulan per film
           sentiment_film.csv    proporsi positif/negatif/netral + niat menonton (EKSPLORATIF)
           top_words.csv         20 kata teratas per film
           network.graphml       jaringan video (buka di Gephi)
           fig_*.png             grafik
           report.md             ringkasan temuan + catatan metodologi
           run_info.json         parameter & versi

Pakai  : python3 analyze_youtube.py [--sets soraya ivanna] [--out results]
"""
import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from emoji_sentiment import emoji_score, extract as extract_emoji  # noqa: E402

# ---------------------------------------------------------------- leksikon (EKSPLORATIF)
# Leksikon kecil buatan sendiri untuk komentar trailer berbahasa Indonesia informal.
# Bukan instrumen tervalidasi: hasilnya hanya untuk eksplorasi awal, bukan klaim utama paper.
POS = set("""
bagus keren mantap mantul seru serem ngeri merinding takut horor gila epic epik
keren banget kerennya bagusnya keren2 suka senang seneng love cinta kangen rindu
terbaik best top juara sukses semangat sehat wow wah gokil anjay jos joss mantab
cantik ganteng cakep luar biasa hebat bangga legend legenda legendaris
""".split())
NEG = set("""
jelek buruk kecewa bosen bosan garing jijik benci males malas basi parah aneh
gak jelas ga jelas sampah lebay alay murahan boring zonk flop gagal sedih
""".split())
INTENT = set("""
nonton bioskop tiket tayang premier premiere gas otw cus wajib harus pasti ditunggu
nunggu menunggu tunggu xxi cgv cinepolis
""".split())
NEGATORS = {"gak", "ga", "nggak", "ngga", "tidak", "tdk", "bukan", "kurang", "enggak", "gk"}
STOP = set("""
yang dan di ke dari ini itu aja ada juga sama untuk buat dengan udah sudah belum bisa
lagi mau kok sih deh dong ya yah yg dgn utk nya aku saya gue gw lu lo kamu kalian
kita kami mereka dia apa kapan kenapa gimana bgt banget jadi tapi atau karena kalau
kalo kayak kaya pas biar pun lah kan tuh nih min admin kak bang mbak mas the a of
to is in and film filmnya trailer trailernya
""".split()) | NEGATORS

TOKEN = re.compile(r"[a-zA-Z]{2,}")


def tokens(text):
    t = str(text).lower()
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)        # "bagusss" -> "baguss"
    return TOKEN.findall(t)


def score(text):
    toks = tokens(text)
    s, prev_neg = 0, False
    for w in toks:
        base = w.rstrip("s") if w not in POS and w.rstrip("s") in POS else w
        if base in POS:
            s += -1 if prev_neg else 1
        elif base in NEG:
            s += 1 if prev_neg else -1
        prev_neg = w in NEGATORS
    s += emoji_score(text)[0]          # emoji ikut menentukan polaritas
    intent = any(w in INTENT for w in toks)
    label = "positif" if s > 0 else "negatif" if s < 0 else "netral"
    return label, intent


# ---------------------------------------------------------------- label film
def film_map(ids_file):
    """Baris komentar '# ...' terakhir sebelum sebuah ID dianggap nama film-nya."""
    m, current = {}, None
    path = BASE / ids_file
    if not path.exists():
        return m
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            label = s.lstrip("#").strip().lstrip("-").strip()
            if label and not label.lower().startswith(("trailer & teaser", "diverifikasi")) \
                    and not re.match(r"^[A-Za-z0-9_-]{11}\s", label):
                current = label
            continue
        vid = re.search(r"(?:v=|youtu\.be/)?([A-Za-z0-9_-]{11})", s)
        if vid:
            m[vid.group(1)] = current
    return m


def short_label(film):
    film = re.sub(r"\s*-\s*MD Pictures", "", film or "")
    film = re.sub(r"^Official (Trailer|Teaser)\s+", "", film, flags=re.I)
    return film.strip() or "Tanpa label"


# ---------------------------------------------------------------- muat data
def load(sets):
    V, C, E = [], [], []
    for name in sets:
        d = BASE / f"yt_{name}"
        if not (d / "videos.csv").exists():
            print(f"[!] {d}/videos.csv tidak ada — jalankan dulu: ./bit scrape {name}")
            continue
        fm = film_map(f"ids_{name}.txt")
        v = pd.read_csv(d / "videos.csv")
        v["set"] = name
        v["film"] = v.video_id.map(fm).fillna(v.title).map(short_label)
        c = pd.read_csv(d / "comments.csv")
        c["set"] = name
        e = pd.read_csv(d / "edges.csv")
        V.append(v), C.append(c), E.append(e)
    if not V:
        sys.exit("Tidak ada data untuk dianalisis.")
    v = pd.concat(V, ignore_index=True)
    c = pd.concat(C, ignore_index=True)
    c = c.merge(v[["video_id", "film", "set"]].drop_duplicates("video_id"), on=["video_id", "set"], how="left")
    e = pd.concat(E, ignore_index=True)
    return v, c, e


# ---------------------------------------------------------------- analisis
def network_metrics(v, c):
    """Bangun ulang jaringan video–video dari komentar gabungan (lintas set)."""
    import networkx as nx
    users = c[c.user != "user_unknown"].groupby("user")["video_id"].apply(lambda s: sorted(set(s)))
    w = Counter()
    for vids in users:
        for a, b in combinations(vids, 2):
            w[(a, b)] += 1
    g = nx.Graph()
    for r in v.itertuples():
        g.add_node(r.video_id, title=str(r.title)[:80], film=r.film, set=r.set,
                   views=int(r.views or 0) if not pd.isna(r.views) else 0)
    for (a, b), k in w.items():
        g.add_edge(a, b, weight=k, distance=1.0 / k)

    deg = dict(g.degree())
    wdeg = dict(g.degree(weight="weight"))
    btw = nx.betweenness_centrality(g, weight="distance", normalized=True) if g.number_of_edges() else {}
    try:
        eig = nx.eigenvector_centrality_numpy(g, weight="weight") if g.number_of_edges() else {}
    except Exception:
        eig = {}
    comms = nx.community.louvain_communities(g, weight="weight", seed=42) if g.number_of_edges() else []
    comm = {n: i + 1 for i, cs in enumerate(sorted(comms, key=len, reverse=True)) for n in cs}
    mod = nx.community.modularity(g, comms, weight="weight") if comms else float("nan")

    for n in g.nodes:
        g.nodes[n]["community"] = comm.get(n, 0)
    stats = {
        "nodes": g.number_of_nodes(), "edges": g.number_of_edges(),
        "density": round(nx.density(g), 4) if g.number_of_nodes() > 1 else 0,
        "components": nx.number_connected_components(g) if g.number_of_nodes() else 0,
        "communities": len(comms), "modularity": round(mod, 4) if not math.isnan(mod) else None,
        "isolates": len(list(nx.isolates(g))),
    }
    m = pd.DataFrame({"video_id": list(g.nodes)})
    m["degree"] = m.video_id.map(deg)
    m["weighted_degree"] = m.video_id.map(wdeg)
    m["betweenness"] = m.video_id.map(btw).fillna(0).round(4)
    m["eigenvector"] = m.video_id.map(eig).fillna(0).round(4)
    m["community"] = m.video_id.map(comm).fillna(0).astype(int)
    return g, m, stats


def film_overlap(c):
    s = c[c.user != "user_unknown"].groupby("film")["user"].apply(set)
    rows = []
    for a, b in combinations(sorted(s.index), 2):
        inter = len(s[a] & s[b])
        union = len(s[a] | s[b])
        rows.append({"film_a": a, "film_b": b, "shared_commenters": inter,
                     "jaccard": round(inter / union, 4) if union else 0})
    return pd.DataFrame(rows).sort_values("shared_commenters", ascending=False)


def comment_time(c):
    ts = pd.to_datetime(c["timestamp"], unit="s", utc=True, errors="coerce") \
        if "timestamp" in c else pd.Series(pd.NaT, index=c.index)
    return ts


# ---------------------------------------------------------------- grafik
def charts(out, vm, fm, ov, sent, g):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[!] matplotlib tidak ada — grafik dilewati")
        return []
    files = []
    INK, MUTED, ACC = "#1f2937", "#6b7280", "#2563eb"
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK,
                         "ytick.color": INK})

    # 1. views per film
    f = fm.sort_values("views_total")
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(f) + 1.2))
    ax.barh(f.film, f.views_total / 1e6, color=ACC)
    for y, x in enumerate(f.views_total / 1e6):
        ax.text(x, y, f" {x:.2f} jt", va="center", color=INK, fontsize=8)
    ax.set_xlabel("Total views trailer (juta)")
    ax.set_title("Total views trailer per film", loc="left", color=INK)
    fig.tight_layout(); p = out / "fig_views_per_film.png"; fig.savefig(p, dpi=160); plt.close(fig); files.append(p)

    # 2. sentimen per film (stacked)
    if not sent.empty:
        s = sent.set_index("film")[["positif", "netral", "negatif"]]
        fig, ax = plt.subplots(figsize=(8, 0.45 * len(s) + 1.2))
        left = pd.Series(0.0, index=s.index)
        for col, colr in (("positif", "#16a34a"), ("netral", "#cbd5e1"), ("negatif", "#dc2626")):
            ax.barh(s.index, s[col], left=left, color=colr, label=col)
            left += s[col]
        ax.set_xlim(0, 1); ax.set_xlabel("Proporsi komentar")
        ax.set_title("Sentimen komentar per film (leksikon eksploratif)", loc="left", color=INK)
        ax.legend(loc="lower right", frameon=False, ncol=3)
        fig.tight_layout(); p = out / "fig_sentiment_per_film.png"; fig.savefig(p, dpi=160); plt.close(fig); files.append(p)

    # 3. heatmap irisan komentator antarfilm
    if not ov.empty:
        films = sorted(set(ov.film_a) | set(ov.film_b))
        mat = pd.DataFrame(0, index=films, columns=films, dtype=int)
        for r in ov.itertuples():
            mat.loc[r.film_a, r.film_b] = mat.loc[r.film_b, r.film_a] = r.shared_commenters
        fig, ax = plt.subplots(figsize=(1.0 + 0.7 * len(films), 0.8 + 0.6 * len(films)))
        im = ax.imshow(mat.values, cmap="Blues")
        ax.set_xticks(range(len(films)), films, rotation=40, ha="right")
        ax.set_yticks(range(len(films)), films)
        for i in range(len(films)):
            for j in range(len(films)):
                if i != j:
                    val = mat.values[i, j]
                    ax.text(j, i, val, ha="center", va="center", fontsize=8,
                            color="white" if val > mat.values.max() * 0.6 else INK)
        ax.set_title("Komentator yang sama antarfilm", loc="left", color=INK)
        fig.colorbar(im, ax=ax, shrink=0.7)
        fig.tight_layout(); p = out / "fig_overlap_film.png"; fig.savefig(p, dpi=160); plt.close(fig); files.append(p)

    # 4. jaringan video
    if g.number_of_edges():
        import networkx as nx
        films = sorted({d["film"] for _, d in g.nodes(data=True)})
        cmap = plt.get_cmap("tab10")
        col = {fname: cmap(i % 10) for i, fname in enumerate(films)}
        pos = nx.spring_layout(g, weight="weight", seed=42, k=0.9)
        fig, ax = plt.subplots(figsize=(9, 7))
        ws = [g[u][v]["weight"] for u, v in g.edges]
        nx.draw_networkx_edges(g, pos, ax=ax, width=[0.4 + 3 * w / max(ws) for w in ws],
                               edge_color="#94a3b8", alpha=0.7)
        vmax = max((d["views"] for _, d in g.nodes(data=True)), default=1) or 1
        nx.draw_networkx_nodes(g, pos, ax=ax, node_color=[col[d["film"]] for _, d in g.nodes(data=True)],
                               node_size=[120 + 900 * d["views"] / vmax for _, d in g.nodes(data=True)],
                               edgecolors="white")
        for fname, cc in col.items():
            ax.scatter([], [], color=cc, label=fname, s=60)
        ax.legend(frameon=False, fontsize=7, loc="upper left", bbox_to_anchor=(1, 1))
        ax.set_title("Jaringan trailer (tebal garis = komentator sama, ukuran = views)", loc="left", color=INK)
        ax.axis("off")
        fig.tight_layout(); p = out / "fig_network.png"; fig.savefig(p, dpi=160); plt.close(fig); files.append(p)
    return files


# ---------------------------------------------------------------- utama
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", nargs="+", default=sorted(d.name[3:] for d in BASE.glob("yt_*") if d.is_dir()))
    ap.add_argument("--out", default="results")
    a = ap.parse_args()

    v, c, e = load(a.sets)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    out = BASE / a.out / f"analysis_{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    print(f"[*] Analisis {len(v)} video, {len(c)} komentar → {out.relative_to(BASE)}")

    # sentimen & niat per komentar
    sc = c["text"].fillna("").map(score) if "text" in c else pd.Series([("netral", False)] * len(c))
    c["sentiment"] = sc.map(lambda x: x[0])
    c["intent"] = sc.map(lambda x: x[1])
    c["ts"] = comment_time(c)

    # jaringan
    g, net, nstats = network_metrics(v, c)

    # metrik video
    per_vid = c.groupby("video_id").agg(
        comments_collected=("comment_id", "count"),
        unique_commenters=("user", "nunique"),
        replies=("is_reply", "sum"),
        share_positive=("sentiment", lambda s: round((s == "positif").mean(), 3)),
        share_negative=("sentiment", lambda s: round((s == "negatif").mean(), 3)),
        share_intent=("intent", lambda s: round(s.mean(), 3)),
    ).reset_index()
    vm = (v.drop(columns=[x for x in ("unique_commenters",) if x in v])
          .merge(per_vid, on="video_id", how="left").merge(net, on="video_id", how="left"))
    vm["like_rate_pct"] = (vm.likes / vm.views * 100).round(3)
    vm["comments_per_10k_views"] = (vm.comments_collected / vm.views * 1e4).round(3)
    vm["hit_cap_500"] = vm.comments_collected >= 500
    vm = vm.sort_values("views", ascending=False)
    vm.to_csv(out / "video_metrics.csv", index=False)

    # metrik film
    fm = vm.groupby(["set", "film"]).agg(
        trailers=("video_id", "count"), views_total=("views", "sum"), likes_total=("likes", "sum"),
        comments_collected=("comments_collected", "sum"),
        first_upload=("upload_date", "min"), last_upload=("upload_date", "max"),
        weighted_degree=("weighted_degree", "sum"),
    ).reset_index()
    uniq = c.groupby("film")["user"].nunique()
    fm["unique_commenters"] = fm.film.map(uniq)
    fm["like_rate_pct"] = (fm.likes_total / fm.views_total * 100).round(3)
    fm = fm.sort_values("views_total", ascending=False)
    fm.to_csv(out / "film_metrics.csv", index=False)

    # irisan antarfilm
    ov = film_overlap(c)
    ov.to_csv(out / "film_overlap.csv", index=False)

    # timeline
    tl = c.dropna(subset=["ts"]).assign(month=lambda d: d.ts.dt.strftime("%Y-%m")) \
        .groupby(["film", "month"]).size().rename("comments").reset_index()
    tl.to_csv(out / "timeline_monthly.csv", index=False)

    # sentimen per film
    sent = c.groupby("film").agg(
        n=("sentiment", "size"),
        positif=("sentiment", lambda s: round((s == "positif").mean(), 3)),
        netral=("sentiment", lambda s: round((s == "netral").mean(), 3)),
        negatif=("sentiment", lambda s: round((s == "negatif").mean(), 3)),
        niat_menonton=("intent", lambda s: round(s.mean(), 3)),
    ).reset_index().sort_values("positif", ascending=False)
    sent.to_csv(out / "sentiment_film.csv", index=False)

    # emoji per film
    c["emojis"] = c["text"].fillna("").map(extract_emoji)
    c["n_emoji"] = c.emojis.map(len)
    erows = []
    for film, grp in c.groupby("film"):
        cnt = Counter(e for l in grp.emojis for e in l)
        erows.append({"film": film, "komentar": len(grp), "total_emoji": int(grp.n_emoji.sum()),
                      "pct_komentar_beremoji": round((grp.n_emoji > 0).mean() * 100, 1),
                      "top10": " ".join(f"{e}{n}" for e, n in cnt.most_common(10))})
    emoji_df = pd.DataFrame(erows).sort_values("total_emoji", ascending=False)
    emoji_df.to_csv(out / "emoji_film.csv", index=False)
    emoji_all = Counter(e for l in c.emojis for e in l)

    # kata teratas
    rows = []
    for film, grp in c.groupby("film"):
        cnt = Counter(w for t in grp["text"].fillna("") for w in tokens(t) if w not in STOP and len(w) > 2)
        rows += [{"film": film, "rank": i + 1, "word": w, "count": n} for i, (w, n) in enumerate(cnt.most_common(20))]
    pd.DataFrame(rows).to_csv(out / "top_words.csv", index=False)

    # graphml
    import networkx as nx
    for n, d in g.nodes(data=True):
        row = vm[vm.video_id == n]
        if len(row):
            d["degree"] = int(row.degree.iloc[0] or 0)
            d["betweenness"] = float(row.betweenness.iloc[0] or 0)
    nx.write_graphml(g, out / "network.graphml")

    figs = charts(out, vm, fm, ov, sent, g)

    # ---------------- laporan
    def md(df, cols, n=10):
        d = df[cols].head(n).copy()
        head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
        return head + "\n".join("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |" for r in d.itertuples(index=False))

    top_edges = []
    for u, w_, d in sorted(g.edges(data=True), key=lambda x: -x[2]["weight"])[:8]:
        top_edges.append(f"| {g.nodes[u]['film']} | {g.nodes[w_]['film']} | {d['weight']} | "
                         f"{'ya' if g.nodes[u]['film'] == g.nodes[w_]['film'] else 'tidak'} |")
    within = sum(d["weight"] for u, w_, d in g.edges(data=True) if g.nodes[u]["film"] == g.nodes[w_]["film"])
    total_w = sum(d["weight"] for *_, d in g.edges(data=True)) or 1
    cap_n = int(vm.hit_cap_500.sum())
    interp = ("Penonton cenderung mengikuti trailer dalam satu film; perpindahan antarfilm lebih jarang."
              if within / total_w >= 0.5 else
              "Sebagian besar keterhubungan justru terjadi antarfilm yang berbeda.")
    n_iv = int((v.set == "ivanna").sum())
    ivanna_note = (f"- Pembanding non-Soraya (Ivanna) hanya {n_iv} trailer — belum cukup untuk perbandingan antar-rumah produksi."
                   if 0 < n_iv < 5 else "")

    report = f"""# Analisis Komentar Trailer YouTube

_Dibuat {datetime.now().strftime('%d-%m-%Y %H:%M')} WIB · set: {', '.join(a.sets)} · {len(v)} video · {len(c):,} komentar · {c.user.nunique():,} komentator unik_

## 1. Ringkasan

- Film dengan total views trailer tertinggi: **{fm.iloc[0].film}** ({fm.iloc[0].views_total/1e6:.2f} juta views dari {int(fm.iloc[0].trailers)} trailer).
- Jaringan trailer: {nstats['nodes']} simpul, {nstats['edges']} edge, kepadatan {nstats['density']}, {nstats['communities']} komunitas (modularitas {nstats['modularity']}), {nstats['isolates']} trailer terisolasi.
- **{within/total_w:.0%}** bobot edge menghubungkan trailer **dari film yang sama**. {interp}
- Pasangan film dengan komentator bersama terbanyak: **{ov.iloc[0].film_a if len(ov) else '-'} ↔ {ov.iloc[0].film_b if len(ov) else '-'}** ({int(ov.iloc[0].shared_commenters) if len(ov) else 0} komentator).

## 2. Metrik per film

{md(fm, ['set', 'film', 'trailers', 'views_total', 'like_rate_pct', 'comments_collected', 'unique_commenters'])}

## 3. Trailer paling sentral di jaringan

{md(vm.sort_values('weighted_degree', ascending=False), ['film', 'title', 'views', 'degree', 'weighted_degree', 'betweenness', 'community'], 8)}

## 4. Edge terkuat

| Film A | Film B | Komentator sama | Film sama? |
|---|---|---|---|
{chr(10).join(top_edges)}

## 5. Irisan komentator antarfilm

{md(ov, ['film_a', 'film_b', 'shared_commenters', 'jaccard'], 10)}

## 6. Sentimen & niat menonton (EKSPLORATIF)

{md(sent, ['film', 'n', 'positif', 'netral', 'negatif', 'niat_menonton'], 12)}

> Sentimen dihitung dengan leksikon kecil buatan sendiri (bahasa Indonesia informal) dengan penanganan negasi sederhana. **Belum divalidasi.** Untuk paper, validasi dengan anotasi manual (mis. 300 komentar, dua anotator, Cohen's κ) atau ganti dengan model tervalidasi (mis. IndoBERT sentiment).

## 7. Emoji

Total **{int(c.n_emoji.sum()):,} emoji** pada {int((c.n_emoji > 0).sum()):,} komentar ({(c.n_emoji > 0).mean():.1%}). Teratas: {"  ".join(f"{e} {n}" for e, n in emoji_all.most_common(15))}

{md(emoji_df, ['film', 'komentar', 'total_emoji', 'pct_komentar_beremoji', 'top10'], 12)}

> Emoji ikut dihitung dalam skor sentimen leksikon (lihat `emoji_sentiment.py`). Emoji ambigu seperti 😂 🤣 😅 😭 😢 😱 dihitung netral karena bisa berarti pujian, ejekan, takut, atau terharu.

## 8. Catatan metodologi & keterbatasan

- Data: yt-dlp, batas 500 komentar per video (termasuk balasan, urutan terbaru). **{cap_n} video** mencapai batas, sehingga untuk video tersebut yang terambil adalah komentar terbaru, bukan seluruh komentar.
- Jaringan: dua trailer terhubung jika ada komentator yang sama; bobot = jumlah komentator sama. Komunitas: Louvain (seed 42). Betweenness memakai jarak = 1/bobot.
- Identitas komentator dipseudonimkan (HMAC-SHA256); teks komentar tidak untuk dipublikasikan ulang.
- `comments_collected` = komentar yang benar-benar terambil dan dianalisis (bukan total komentar publik di YouTube).
- `like_rate_pct` bergantung pada jumlah like yang ditampilkan YouTube; trailer yang menyembunyikan like akan terlihat rendah.
- Leksikon memperlakukan kata seperti "serem", "ngeri", "merinding" sebagai positif (pujian untuk film horor). Asumsi ini perlu diuji saat validasi.
{ivanna_note}

## 9. Berkas

{chr(10).join('- `' + p.name + '`' for p in sorted(out.iterdir()) if p.suffix in ('.csv', '.graphml', '.png'))}
"""
    (out / "report.md").write_text(report, encoding="utf-8")
    import networkx, matplotlib  # noqa
    (out / "run_info.json").write_text(json.dumps({
        "created_local": datetime.now().isoformat(timespec="seconds"),
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sets": a.sets, "n_videos": len(v), "n_comments": len(c), "n_commenters": int(c.user.nunique()),
        "network": nstats, "louvain_seed": 42, "sentiment": "lexicon v0 (exploratory, unvalidated)",
        "versions": {"pandas": pd.__version__, "networkx": networkx.__version__,
                     "matplotlib": matplotlib.__version__, "python": sys.version.split()[0]},
    }, indent=2, ensure_ascii=False))

    print(f"✅ Selesai: {len(list(out.iterdir()))} berkas")
    print(f"   Laporan : {out / 'report.md'}")
    for p in figs:
        print(f"   Grafik  : {p.name}")
    print(f"\nRingkasan: {within/total_w:.0%} bobot jaringan ada di dalam film yang sama · "
          f"{nstats['communities']} komunitas · film teratas: {fm.iloc[0].film}")


if __name__ == "__main__":
    main()
