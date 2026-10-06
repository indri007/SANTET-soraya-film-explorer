#!/usr/bin/env python3
"""
ytdlp_to_csv.py — ubah hasil yt-dlp (*.info.json dengan komentar) menjadi
videos.csv, comments.csv (komentator dianonimkan), dan edges.csv
(dua video terhubung kalau dikomentari pengguna yang sama).

Pakai:
  python3 ytdlp_to_csv.py <folder_info_json> [--salt "kalimat-rahasia"] [--no-text]
"""
import argparse
import hashlib
import hmac
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    pass


def anon(author_id, salt):
    if not author_id:
        return "user_unknown"
    return "user_" + hmac.new(salt.encode(), str(author_id).encode(), hashlib.sha256).hexdigest()[:12]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("folder")
    p.add_argument("--salt", default="ganti-dengan-kalimat-rahasia")
    p.add_argument("--no-text", action="store_true")
    a = p.parse_args()

    folder = Path(a.folder)
    files = sorted(folder.glob("*.info.json"))
    if not files:
        raise SystemExit(f"Tidak ada *.info.json di {folder}")

    videos, comments = [], []
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("_type") == "playlist":
            continue
        videos.append({
            "video_id": d.get("id"),
            "title": d.get("title"),
            "channel": d.get("channel") or d.get("uploader"),
            "upload_date": d.get("upload_date"),
            "duration_s": d.get("duration"),
            "views": d.get("view_count"),
            "likes": d.get("like_count"),
            "comment_count": d.get("comment_count"),
            "url": d.get("webpage_url"),
        })
        for c in d.get("comments") or []:
            parent = c.get("parent")
            comments.append({
                "comment_id": c.get("id"),
                "video_id": d.get("id"),
                "parent_id": None if parent in (None, "root") else parent,
                "is_reply": parent not in (None, "root"),
                "user": anon(c.get("author_id"), a.salt),
                "timestamp": c.get("timestamp"),
                "like_count": c.get("like_count"),
                "text": None if a.no_text else c.get("text"),
            })

    v = pd.DataFrame(videos)
    c = pd.DataFrame(comments)

    counts = {}
    if not c.empty:
        per_user = c[c.user != "user_unknown"].groupby("user")["video_id"].apply(lambda s: sorted(set(s)))
        for vids in per_user:
            for x, y in itertools.combinations(vids, 2):
                counts[(x, y)] = counts.get((x, y), 0) + 1
    e = pd.DataFrame([{"vertex_1": x, "vertex_2": y, "shared_users": w} for (x, y), w in counts.items()],
                     columns=["vertex_1", "vertex_2", "shared_users"]).sort_values("shared_users", ascending=False)

    if not c.empty:
        v["unique_commenters"] = v.video_id.map(c.groupby("video_id")["user"].nunique()).fillna(0).astype(int)

    v.to_csv(folder / "videos.csv", index=False)
    c.to_csv(folder / "comments.csv", index=False)
    e.to_csv(folder / "edges.csv", index=False)
    (folder / "run_info.json").write_text(json.dumps({
        "converted_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "yt-dlp info.json", "n_videos": len(v), "n_comments": len(c), "n_edges": len(e),
        "anonymization": "HMAC-SHA256(author_id, salt)[:12]",
    }, indent=2))
    print(f"✅ {len(v)} video · {len(c)} komentar · {len(e)} edge → {folder}")


if __name__ == "__main__":
    main()
