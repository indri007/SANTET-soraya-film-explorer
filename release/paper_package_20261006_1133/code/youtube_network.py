#!/usr/bin/env python3
"""
youtube_network.py — padanan script untuk "NodeXL > Import from YouTube Video Network".

Mengambil video (lewat kata kunci ATAU daftar video ID), statistik video, komentar + balasan,
lalu membangun jaringan video–video: dua video terhubung kalau dikomentari oleh pengguna yang sama
(setara opsi NodeXL "Pair of videos commented on by the same user").

Username/ID channel komentator DIANONIMKAN (HMAC-SHA256 + salt) demi etika riset.

Persiapan:
  pip install --break-system-packages requests pandas openpyxl networkx
  export YT_API_KEY="AIza..."          # YouTube Data API v3 key (Google Cloud Console)
  export YT_SALT="kalimat-rahasia-anda"  # untuk anonimisasi; simpan, jangan di-commit

Contoh:
  # Opsi B (disarankan): daftar video ID trailer resmi, satu per baris
  python3 youtube_network.py --ids-file ids_ivanna.txt --tag ivanna

  # Opsi A: kata kunci, dibatasi ke kanal resmi Soraya (lebih bersih)
  python3 youtube_network.py --query "Soraya Intercine Films trailer" \
      --channel-id UCxxxxxxxxxxxxxxxxxxxx --tag soraya_all

  # Banyak judul sekaligus (satu run per judul), dari file judul
  python3 youtube_network.py --titles-file judul_soraya.txt
"""
import argparse
import hashlib
import hmac
import itertools
import json
import os
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import requests

API = "https://www.googleapis.com/youtube/v3"
QUOTA = {"search": 100, "videos": 1, "commentThreads": 1, "comments": 1}
quota_used = 0


# ------------------------------------------------------------------ API
def call(endpoint: str, params: dict, key: str, retries: int = 4) -> dict:
    global quota_used
    params = {k: v for k, v in {**params, "key": key}.items() if v is not None}
    for attempt in range(retries):
        r = requests.get(f"{API}/{endpoint}", params=params, timeout=30)
        quota_used += QUOTA.get(endpoint, 1)
        if r.status_code == 200:
            return r.json()
        try:
            err = r.json().get("error", {})
        except ValueError:
            err = {}
        reason = (err.get("errors") or [{}])[0].get("reason", "")
        if reason in ("commentsDisabled", "videoNotFound", "forbidden", "commentThreadNotFound"):
            return {"_skip": reason}
        if reason in ("quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded"):
            sys.exit(f"\n⛔ Kuota API habis ({reason}). Lanjutkan besok atau pakai key lain. "
                     f"Perkiraan kuota terpakai: {quota_used} unit.")
        if r.status_code >= 500 or r.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        sys.exit(f"\n⛔ Error {r.status_code} di {endpoint}: {err.get('message', r.text[:200])}")
    sys.exit(f"\n⛔ {endpoint} gagal setelah {retries} kali coba.")


def rfc3339(d: str, end: bool = False) -> str:
    return f"{d}T23:59:59Z" if end else f"{d}T00:00:00Z"


# ------------------------------------------------------------------ Video
def search_videos(q, after, before, order, limit, channel_id, key):
    ids, token = [], None
    while len(ids) < limit:
        d = call("search", {
            "part": "id", "q": q, "type": "video", "order": order,
            "maxResults": min(50, limit - len(ids)),
            "publishedAfter": rfc3339(after), "publishedBefore": rfc3339(before, end=True),
            "channelId": channel_id, "regionCode": "ID", "relevanceLanguage": "id",
            "pageToken": token,
        }, key)
        ids += [it["id"]["videoId"] for it in d.get("items", []) if "videoId" in it.get("id", {})]
        token = d.get("nextPageToken")
        if not token:
            break
    return list(dict.fromkeys(ids))[:limit]


def read_ids(path):
    ids = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", line)
        ids.append(m.group(1) if m else line[:11])
    return list(dict.fromkeys(ids))


def video_details(ids, key):
    rows = []
    for i in range(0, len(ids), 50):
        d = call("videos", {"part": "snippet,statistics,contentDetails",
                            "id": ",".join(ids[i:i + 50])}, key)
        for it in d.get("items", []):
            s, st = it["snippet"], it.get("statistics", {})
            rows.append({
                "video_id": it["id"],
                "title": s.get("title"),
                "channel_title": s.get("channelTitle"),
                "channel_id": s.get("channelId"),
                "published_at": s.get("publishedAt"),
                "duration": it.get("contentDetails", {}).get("duration"),
                "views": int(st.get("viewCount", 0)),
                "likes": int(st.get("likeCount", 0)) if "likeCount" in st else None,
                "comment_count": int(st.get("commentCount", 0)) if "commentCount" in st else None,
                "tags": "|".join(s.get("tags", [])),
                "url": f"https://www.youtube.com/watch?v={it['id']}",
            })
    return rows


# ------------------------------------------------------------------ Komentar
def anon(channel_id: str, salt: str) -> str:
    if not channel_id:
        return "user_unknown"
    return "user_" + hmac.new(salt.encode(), channel_id.encode(), hashlib.sha256).hexdigest()[:12]


def comment_row(c, video_id, parent_id, salt, keep_text):
    s = c["snippet"]
    return {
        "comment_id": c["id"],
        "video_id": video_id,
        "parent_id": parent_id,
        "is_reply": parent_id is not None,
        "user": anon(s.get("authorChannelId", {}).get("value"), salt),
        "published_at": s.get("publishedAt"),
        "like_count": s.get("likeCount", 0),
        "text": s.get("textOriginal") if keep_text else None,
    }


def fetch_replies(parent_id, limit, key):
    out, token = [], None
    while len(out) < limit:
        d = call("comments", {"part": "snippet", "parentId": parent_id, "maxResults": 100,
                              "textFormat": "plainText", "pageToken": token}, key)
        if "_skip" in d:
            break
        out += d.get("items", [])
        token = d.get("nextPageToken")
        if not token:
            break
    return out[:limit]


def fetch_comments(video_id, max_comments, max_replies, key, salt, keep_text):
    rows, token, n_top = [], None, 0
    while n_top < max_comments:
        d = call("commentThreads", {"part": "snippet,replies", "videoId": video_id,
                                    "maxResults": 100, "order": "relevance",
                                    "textFormat": "plainText", "pageToken": token}, key)
        if "_skip" in d:
            return rows, d["_skip"]
        for th in d.get("items", []):
            if n_top >= max_comments:
                break
            top = th["snippet"]["topLevelComment"]
            n_top += 1
            rows.append(comment_row(top, video_id, None, salt, keep_text))
            total = th["snippet"].get("totalReplyCount", 0)
            if total and max_replies:
                reps = th.get("replies", {}).get("comments", [])
                if total > len(reps):                      # API hanya menyertakan ≤5 balasan
                    reps = fetch_replies(top["id"], max_replies, key)
                for rp in reps[:max_replies]:
                    rows.append(comment_row(rp, video_id, top["id"], salt, keep_text))
        token = d.get("nextPageToken")
        if not token:
            break
    return rows, "ok"


# ------------------------------------------------------------------ Jaringan
def build_edges(comments: pd.DataFrame) -> pd.DataFrame:
    """Edge video–video, bobot = jumlah pengguna unik yang mengomentari keduanya."""
    if comments.empty:
        return pd.DataFrame(columns=["vertex_1", "vertex_2", "shared_users"])
    per_user = (comments[comments.user != "user_unknown"]
                .groupby("user")["video_id"].apply(lambda s: sorted(set(s))))
    counts = {}
    for vids in per_user:
        for a, b in itertools.combinations(vids, 2):
            counts[(a, b)] = counts.get((a, b), 0) + 1
    return (pd.DataFrame([{"vertex_1": a, "vertex_2": b, "shared_users": w}
                          for (a, b), w in counts.items()])
            .sort_values("shared_users", ascending=False, ignore_index=True)
            if counts else pd.DataFrame(columns=["vertex_1", "vertex_2", "shared_users"]))


def save_graphml(videos, edges, path):
    try:
        import networkx as nx
    except ImportError:
        print("  (networkx tidak terpasang — GraphML dilewati)")
        return
    g = nx.Graph()
    for v in videos.to_dict("records"):
        g.add_node(v["video_id"], **{k: ("" if pd.isna(x) else x) for k, x in v.items()
                                     if k in ("title", "channel_title", "published_at", "views")})
    for e in edges.to_dict("records"):
        g.add_edge(e["vertex_1"], e["vertex_2"], weight=int(e["shared_users"]))
    nx.write_graphml(g, path)


# ------------------------------------------------------------------ Satu run
def run(args, key, salt, query=None, ids=None, tag="run"):
    global quota_used
    quota_used = 0
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    out = Path(args.out) / f"{tag}_{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {tag} ===")

    if ids is None:
        ids = search_videos(query, args.after, args.before, args.order,
                            args.max_videos, args.channel_id, key)
    print(f"  Video: {len(ids)}")
    videos = pd.DataFrame(video_details(ids, key))
    if videos.empty:
        print("  Tidak ada video ditemukan.")
        return

    all_comments, status = [], {}
    for i, vid in enumerate(videos.video_id, 1):
        rows, st = fetch_comments(vid, args.max_comments, args.max_replies, key, salt, not args.no_text)
        all_comments += rows
        status[vid] = st
        print(f"  [{i}/{len(videos)}] {vid}: {len(rows)} komentar ({st})")
    comments = pd.DataFrame(all_comments)
    edges = build_edges(comments)

    users_per_video = comments.groupby("video_id")["user"].nunique() if not comments.empty else {}
    videos["unique_commenters"] = videos.video_id.map(users_per_video).fillna(0).astype(int)
    videos["comment_status"] = videos.video_id.map(status)

    meta = {
        "tag": tag, "query": query, "n_input_ids": None if query else len(ids),
        "channel_id": args.channel_id, "published_after": args.after,
        "published_before": args.before, "order": args.order,
        "max_videos": args.max_videos, "max_comments_per_video": args.max_comments,
        "max_replies_per_thread": args.max_replies, "comment_text_kept": not args.no_text,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "api": "YouTube Data API v3", "estimated_quota_units": quota_used,
        "n_videos": len(videos), "n_comments": len(comments), "n_edges": len(edges),
        "anonymization": "HMAC-SHA256(authorChannelId, salt)[:12]",
    }

    videos.to_csv(out / "videos.csv", index=False)
    comments.to_csv(out / "comments.csv", index=False)
    edges.to_csv(out / "edges.csv", index=False)
    (out / "run_info.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    with pd.ExcelWriter(out / f"{tag}.xlsx") as xw:                    # mirip workbook NodeXL
        edges.to_excel(xw, sheet_name="Edges", index=False)
        videos.to_excel(xw, sheet_name="Vertices", index=False)
        comments.to_excel(xw, sheet_name="Comments", index=False)
        pd.DataFrame(meta.items(), columns=["key", "value"]).to_excel(xw, sheet_name="Run Info", index=False)
    save_graphml(videos, edges, out / f"{tag}.graphml")

    print(f"  ✅ {len(videos)} video · {len(comments)} komentar · {len(edges)} edge "
          f"· ±{quota_used} unit kuota\n  → {out}")


# ------------------------------------------------------------------ CLI
def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40] or "run"


def main():
    p = argparse.ArgumentParser(description="YouTube video network (NodeXL-style) untuk riset film.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--query", help="kata kunci pencarian (Opsi A)")
    src.add_argument("--ids-file", help="file berisi video ID/URL, satu per baris (Opsi B)")
    src.add_argument("--titles-file", help="file berisi judul film, satu per baris → satu run per judul")
    p.add_argument("--channel-id", help="batasi pencarian ke satu kanal (mis. kanal resmi Soraya)")
    p.add_argument("--after", default="2020-01-01")
    p.add_argument("--before", default=date.today().isoformat())
    p.add_argument("--order", default="viewCount",
                   choices=["viewCount", "relevance", "date", "rating", "title"])
    p.add_argument("--max-videos", type=int, default=100)
    p.add_argument("--max-comments", type=int, default=500, help="komentar utama per video")
    p.add_argument("--max-replies", type=int, default=100, help="balasan per thread komentar")
    p.add_argument("--no-text", action="store_true", help="jangan simpan isi komentar")
    p.add_argument("--tag", help="nama run / folder output")
    p.add_argument("--out", default="data/youtube")
    args = p.parse_args()

    key = os.getenv("YT_API_KEY")
    salt = os.getenv("YT_SALT")
    if not key:
        sys.exit("⛔ Set dulu: export YT_API_KEY=\"AIza...\"")
    if not salt:
        sys.exit("⛔ Set dulu: export YT_SALT=\"kalimat-rahasia\" (untuk anonimisasi komentator)")

    if args.ids_file:
        run(args, key, salt, ids=read_ids(args.ids_file), tag=args.tag or slug(Path(args.ids_file).stem))
    elif args.query:
        run(args, key, salt, query=args.query, tag=args.tag or slug(args.query))
    else:
        titles = [t.strip() for t in Path(args.titles_file).read_text(encoding="utf-8").splitlines()
                  if t.strip() and not t.startswith("#")]
        print(f"{len(titles)} judul. Perkiraan kuota pencarian: {len(titles) * 100 * -(-args.max_videos // 50)} unit.")
        for t in titles:
            run(args, key, salt, query=t, tag=slug(t))


if __name__ == "__main__":
    main()
