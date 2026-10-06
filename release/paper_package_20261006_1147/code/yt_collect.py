#!/usr/bin/python3
"""
yt_collect.py — Kumpulkan data YouTube (video + komentar + balasan) per film.

Contoh:
  export YT_API_KEY="AIza..."           # Windows: set YT_API_KEY=AIza...
  python yt_collect.py --films films.csv --out data/youtube --max-videos 10

Output (CSV, append & bisa dilanjutkan / resume):
  data/youtube/videos.csv     -> 1 baris per video
  data/youtube/comments.csv   -> 1 baris per komentar & balasan (sumber utama 1 juta baris)
  data/youtube/progress.json  -> video yang sudah selesai (untuk resume)

Biaya kuota (default 10.000 unit/hari):
  search.list = 100 unit | videos.list = 1 unit | commentThreads.list = 1 unit/100 komentar
  -> ±1 juta komentar ≈ 10.000–15.000 unit (1–2 hari kuota).
"""
import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    pass

VIDEO_FIELDS = ["film", "video_id", "title", "channel_id", "channel_title", "published_at",
                "duration", "view_count", "like_count", "comment_count", "query", "retrieved_at"]
COMMENT_FIELDS = ["film", "video_id", "comment_id", "parent_id", "is_reply", "author_hash",
                  "parent_author_hash", "text", "like_count", "reply_count", "published_at",
                  "retrieved_at"]

QUOTA = {"used": 0}


def now():
    return datetime.now(timezone.utc).isoformat()


def h(value: str) -> str:
    """Samarkan identitas komentator (UU PDP)."""
    return hashlib.sha256((value or "").encode()).hexdigest()[:16]


def call(req, cost):
    """Eksekusi request dengan retry + backoff."""
    for attempt in range(6):
        try:
            res = req.execute()
            QUOTA["used"] += cost
            return res
        except HttpError as e:
            status = e.resp.status
            reason = str(e)
            if status == 403 and "quotaExceeded" in reason:
                print(f"\n[STOP] Kuota habis (~{QUOTA['used']} unit). Jalankan lagi besok — progres tersimpan.")
                sys.exit(2)
            if status == 403 and "commentsDisabled" in reason:
                return None
            if status in (500, 503, 429):
                time.sleep(2 ** attempt)
                continue
            if status == 404:
                return None
            raise
    return None


def open_writer(path, fields):
    exists = os.path.exists(path)
    f = open(path, "a", newline="", encoding="utf-8")
    w = csv.DictWriter(f, fieldnames=fields)
    if not exists:
        w.writeheader()
    return f, w


def search_videos(yt, query, max_results):
    res = call(yt.search().list(part="id", q=query, type="video", regionCode="ID",
                                relevanceLanguage="id", maxResults=min(max_results, 50)), 100)
    return [it["id"]["videoId"] for it in (res or {}).get("items", [])]


def video_details(yt, ids):
    out = []
    for i in range(0, len(ids), 50):
        res = call(yt.videos().list(part="snippet,statistics,contentDetails",
                                    id=",".join(ids[i:i + 50])), 1)
        out.extend((res or {}).get("items", []))
    return out


def fetch_replies(yt, parent_id):
    token = None
    while True:
        res = call(yt.comments().list(part="snippet", parentId=parent_id, maxResults=100,
                                      pageToken=token, textFormat="plainText"), 1)
        if not res:
            return
        for it in res.get("items", []):
            yield it
        token = res.get("nextPageToken")
        if not token:
            return


def fetch_comments(yt, film, video_id, writer, with_replies=True):
    token, n = None, 0
    while True:
        res = call(yt.commentThreads().list(part="snippet,replies", videoId=video_id, maxResults=100,
                                            pageToken=token, textFormat="plainText", order="time"), 1)
        if not res:
            return n
        for th in res.get("items", []):
            top = th["snippet"]["topLevelComment"]
            s = top["snippet"]
            parent_author = h(s.get("authorChannelId", {}).get("value", s.get("authorDisplayName", "")))
            writer.writerow({
                "film": film, "video_id": video_id, "comment_id": top["id"], "parent_id": "",
                "is_reply": 0, "author_hash": parent_author, "parent_author_hash": "",
                "text": s.get("textDisplay", ""), "like_count": s.get("likeCount", 0),
                "reply_count": th["snippet"].get("totalReplyCount", 0),
                "published_at": s.get("publishedAt"), "retrieved_at": now()})
            n += 1
            total_replies = th["snippet"].get("totalReplyCount", 0)
            if with_replies and total_replies:
                # Balasan yang ikut di thread maksimal 5; ambil lengkap jika lebih.
                replies = (th.get("replies", {}).get("comments", []) if total_replies <= 5
                           else fetch_replies(yt, top["id"]))
                for r in replies:
                    rs = r["snippet"]
                    writer.writerow({
                        "film": film, "video_id": video_id, "comment_id": r["id"],
                        "parent_id": top["id"], "is_reply": 1,
                        "author_hash": h(rs.get("authorChannelId", {}).get("value", rs.get("authorDisplayName", ""))),
                        "parent_author_hash": parent_author, "text": rs.get("textDisplay", ""),
                        "like_count": rs.get("likeCount", 0), "reply_count": 0,
                        "published_at": rs.get("publishedAt"), "retrieved_at": now()})
                    n += 1
        token = res.get("nextPageToken")
        if not token:
            return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--films", default="films.csv")
    ap.add_argument("--out", default="data/youtube")
    ap.add_argument("--max-videos", type=int, default=10, help="video per query pencarian")
    ap.add_argument("--extra-queries", default="trailer,review,reaction",
                    help="kata tambahan per judul, dipisah koma")
    ap.add_argument("--no-replies", action="store_true")
    ap.add_argument("--target", type=int, default=1_000_000, help="berhenti setelah N komentar")
    args = ap.parse_args()

    key = os.environ.get("YT_API_KEY")
    if not key:
        sys.exit("Set dulu environment variable YT_API_KEY.")
    
    yt = build("youtube", "v3", developerKey=key, cache_discovery=False)
    os.makedirs(args.out, exist_ok=True)

    prog_path = os.path.join(args.out, "progress.json")
    done = set(json.load(open(prog_path))) if os.path.exists(prog_path) else set()
    vf, vw = open_writer(os.path.join(args.out, "videos.csv"), VIDEO_FIELDS)
    cf, cw = open_writer(os.path.join(args.out, "comments.csv"), COMMENT_FIELDS)

    total = 0
    with open(args.films, encoding="utf-8") as f:
        films = list(csv.DictReader(f))

    try:
        for film in films:
            title = film["judul"]
            ids = [v.strip() for v in (film.get("video_ids") or "").split("|") if v.strip()]
            queries = [f"{title} {x.strip()}" for x in args.extra_queries.split(",") if x.strip()]
            if not ids:
                for q in queries:
                    ids += [v for v in search_videos(yt, q, args.max_videos) if v not in ids]
            for v in video_details(yt, [i for i in ids if i not in done]):
                s, st = v["snippet"], v.get("statistics", {})
                vw.writerow({"film": title, "video_id": v["id"], "title": s["title"],
                             "channel_id": s["channelId"], "channel_title": s["channelTitle"],
                             "published_at": s["publishedAt"],
                             "duration": v["contentDetails"]["duration"],
                             "view_count": st.get("viewCount"), "like_count": st.get("likeCount"),
                             "comment_count": st.get("commentCount"),
                             "query": "|".join(queries), "retrieved_at": now()})
                vf.flush()
                n = fetch_comments(yt, title, v["id"], cw, with_replies=not args.no_replies)
                cf.flush()
                total += n
                done.add(v["id"])
                json.dump(sorted(done), open(prog_path, "w"))
                print(f"{title[:35]:35} | {v['id']} | +{n:>7,} komentar | total {total:,} | kuota ~{QUOTA['used']:,}")
                if total >= args.target:
                    print("Target tercapai.")
                    return
    finally:
        vf.close()
        cf.close()


if __name__ == "__main__":
    main()
