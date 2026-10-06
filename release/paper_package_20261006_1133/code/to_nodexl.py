#!/usr/bin/python3
"""
to_nodexl.py — Ubah comments.csv menjadi edge list yang bisa diimpor NodeXL
(NodeXL > Data > Import > From Open Workbook / From Text).

Contoh:
  python to_nodexl.py --comments data/youtube/comments.csv --film "The Doll 3" --out nodexl_thedoll3.xlsx

Dua jenis edge:
  reply   : author_hash (yang membalas)  -> parent_author_hash (yang dibalas)
  comment : author_hash                  -> video_id (komentar langsung ke video)

Batas Excel 1.048.576 baris -> gunakan --film / --max-edges untuk sub-jaringan.
"""
import argparse
import csv
import os
import sys

EXCEL_LIMIT = 1_048_575


def process_with_pandas(args):
    import pandas as pd
    df = pd.read_csv(args.comments, dtype=str)
    if args.film:
        df = df[df["film"] == args.film]

    replies = df[df["is_reply"] == "1"].assign(
        **{"Vertex 1": lambda d: d["author_hash"], "Vertex 2": lambda d: d["parent_author_hash"],
           "Relationship": "reply"})
    edges = [replies]
    if not args.replies_only:
        tops = df[df["is_reply"] == "0"].assign(
            **{"Vertex 1": lambda d: d["author_hash"], "Vertex 2": lambda d: "VIDEO_" + d["video_id"],
               "Relationship": "comment"})
        edges.append(tops)

    cols = ["Vertex 1", "Vertex 2", "Relationship", "film", "video_id", "text", "like_count", "published_at"]
    out = pd.concat(edges)[cols]
    limit = min(args.max_edges, EXCEL_LIMIT)
    if len(out) > limit:
        print(f"{len(out):,} edge > batas {limit:,}; diambil {limit:,} edge dengan like terbanyak.")
        out = out.assign(_l=pd.to_numeric(out["like_count"], errors="coerce").fillna(0)) \
                 .nlargest(limit, "_l").drop(columns="_l")
    out["text"] = out["text"].fillna("").str.slice(0, 32000)  # batas sel Excel
    
    try:
        out.to_excel(args.out, index=False, sheet_name="Edges")
        vertices_count = pd.unique(out[['Vertex 1', 'Vertex 2']].values.ravel()).size
        print(f"Tersimpan {args.out}: {len(out):,} edge, {vertices_count:,} vertex.")
    except Exception:
        csv_out = args.out.replace(".xlsx", ".csv")
        out.to_csv(csv_out, index=False, encoding="utf-8")
        vertices_count = pd.unique(out[['Vertex 1', 'Vertex 2']].values.ravel()).size
        print(f"[NOTE] Tersimpan sebagai format teks NodeXL {csv_out}: {len(out):,} edge, {vertices_count:,} vertex.")


def process_with_csv(args):
    """Fallback parser menggunakan standard library csv bila pandas belum diinstal."""
    edges = []
    vertices = set()

    with open(args.comments, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if args.film and row.get("film") != args.film:
                continue

            author = row.get("author_hash", "")
            is_reply = str(row.get("is_reply", "0")).strip()
            parent_author = row.get("parent_author_hash", "")
            video_id = row.get("video_id", "")
            text = (row.get("text", "") or "")[:32000]
            like_count = row.get("like_count", "0")
            pub_at = row.get("published_at", "")
            film = row.get("film", "")

            if is_reply == "1" and parent_author:
                edges.append({
                    "Vertex 1": author,
                    "Vertex 2": parent_author,
                    "Relationship": "reply",
                    "film": film,
                    "video_id": video_id,
                    "text": text,
                    "like_count": like_count,
                    "published_at": pub_at
                })
                vertices.add(author)
                vertices.add(parent_author)
            elif not args.replies_only:
                target_video = f"VIDEO_{video_id}"
                edges.append({
                    "Vertex 1": author,
                    "Vertex 2": target_video,
                    "Relationship": "comment",
                    "film": film,
                    "video_id": video_id,
                    "text": text,
                    "like_count": like_count,
                    "published_at": pub_at
                })
                vertices.add(author)
                vertices.add(target_video)

    out_csv = args.out if args.out.endswith(".csv") else args.out.replace(".xlsx", ".csv")
    with open(out_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Vertex 1", "Vertex 2", "Relationship", "film", "video_id", "text", "like_count", "published_at"
        ])
        writer.writeheader()
        for edge in edges:
            writer.writerow(edge)

    print(f"Tersimpan {out_csv} (kompatibel NodeXL Pro 'From Text'): {len(edges):,} edge, {len(vertices):,} vertex.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--comments", default="data/youtube/comments.csv")
    ap.add_argument("--film", default=None, help="filter satu film")
    ap.add_argument("--replies-only", action="store_true", help="hanya jaringan balas-membalas")
    ap.add_argument("--max-edges", type=int, default=200_000)
    ap.add_argument("--out", default="nodexl_edges.xlsx")
    args = ap.parse_args()

    if not os.path.exists(args.comments):
        print(f"[!] File komentar belum ditemukan di: {args.comments}")
        print("    Jalankan pengumpulan terlebih dahulu dengan: python yt_collect.py")
        sys.exit(1)

    try:
        import pandas as pd
        process_with_pandas(args)
    except ImportError:
        process_with_csv(args)


if __name__ == "__main__":
    main()
