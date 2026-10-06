"""
Crawler: Caption + Komentar Instagram Indonesia (Hashtag Trending, Niche, Aktor/Publik Figur)
Target: ~10.000 data (caption + komentar gabungan), periode >= 2020
Output: CSV siap pakai untuk pipeline IndoBERT + BERTopic, plus graf interaksi (mentions & co-hashtag)

PENTING - baca dulu:
1. Instagram TIDAK bisa "dicari mundur ke tahun 2020" secara bebas. Yang diambil adalah
   POSTINGAN YANG MASIH ADA SEKARANG dari hashtag/akun target, lalu difilter tanggalnya >= 2020.
   Postingan yang sudah dihapus/akun private tidak akan muncul.
2. Instagram SANGAT ketat rate-limit. Script ini otomatis pakai delay antar-request.
   Untuk 10.000 data, jalankan bertahap (bisa berjam-jam / beberapa hari), JANGAN dipaksa sekali jalan.
3. Instaloader tanpa login dibatasi lebih ketat. Login dengan akun kamu sendiri disarankan
   (JANGAN pakai akun utama - pakai akun sekunder untuk riset, risiko kena rate-limit/flag).
4. Hormati privasi: hanya ambil dari akun PUBLIK. Jangan crawl akun privat.

Install:
    pip install instaloader pandas networkx --break-system-packages
"""

import re
import time
import random
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import networkx as nx
import instaloader


# =========================================================
# 1. KONFIGURASI - EDIT SESUAI KEBUTUHAN
# =========================================================

# Login opsional tapi disarankan (akun sekunder, bukan akun utama)
IG_USERNAME = None   # isi "username_kamu" kalau mau login, atau biarkan None
IG_PASSWORD = None   # isi password, atau biarkan None (akan diminta interaktif kalau IG_USERNAME diisi)

# Hashtag trending yang mau di-crawl (ganti sesuai topik risetmu)
HASHTAGS = [
    "indonesia",
    "viral",
    "trending",
    # tambahkan hashtag lain di sini
]

# Akun niche (contoh: akun komunitas/topik spesifik - ganti sesuai kebutuhan)
NICHE_ACCOUNTS = [
    # "nama_akun_niche_1",
    # "nama_akun_niche_2",
]

# Akun aktor/publik figur (ganti sesuai kebutuhan - HANYA akun publik)
ACTOR_ACCOUNTS = [
    # "nama_akun_aktor_1",
    # "nama_akun_aktor_2",
]

MIN_DATE = datetime(2020, 1, 1)          # filter tanggal minimum
TARGET_TOTAL = 10_000                     # target jumlah baris data (caption + komentar)
MAX_POSTS_PER_SOURCE = 200                # batas post per hashtag/akun (biar merata & tidak kena limit)
MAX_COMMENTS_PER_POST = 30                # batas komentar diambil per post

DELAY_MIN = 3      # jeda antar-request (detik) - JANGAN diperkecil, resiko kena block
DELAY_MAX = 7

OUTPUT_DIR = Path("data")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_CSV = OUTPUT_DIR / "instagram_crawled_data.csv"
CHECKPOINT_JSON = OUTPUT_DIR / "crawl_checkpoint.json"   # simpan progress biar bisa dilanjut


# =========================================================
# 2. SETUP INSTALOADER
# =========================================================
def init_loader():
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,   # kita ambil komentar manual biar bisa dibatasi jumlahnya
        save_metadata=False,
        compress_json=False,
    )
    if IG_USERNAME:
        try:
            L.load_session_from_file(IG_USERNAME)
            print(f"[INFO] Sesi login '{IG_USERNAME}' dimuat dari cache.")
        except FileNotFoundError:
            L.login(IG_USERNAME, IG_PASSWORD)
            L.save_session_to_file()
            print(f"[INFO] Login baru sebagai '{IG_USERNAME}', sesi disimpan.")
    return L


def polite_delay():
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


# =========================================================
# 3. UTILITAS
# =========================================================
def extract_mentions(text: str):
    return re.findall(r"@(\w+)", text or "")


def extract_hashtags(text: str):
    return re.findall(r"#(\w+)", text or "")


def load_checkpoint():
    if CHECKPOINT_JSON.exists():
        with open(CHECKPOINT_JSON, "r") as f:
            return json.load(f)
    return {"processed_sources": [], "rows_collected": 0}


def save_checkpoint(state):
    with open(CHECKPOINT_JSON, "w") as f:
        json.dump(state, f)


# =========================================================
# 4. CRAWLING PER SUMBER (hashtag / akun)
# =========================================================
def crawl_posts_from_iterator(post_iterator, source_type: str, source_name: str,
                               rows: list, max_posts: int):
    count = 0
    for post in post_iterator:
        if count >= max_posts:
            break
        if len(rows) >= TARGET_TOTAL:
            break

        post_date = post.date_utc
        if post_date < MIN_DATE:
            # hashtag/explore biasanya urut dari terbaru; kalau sudah lewat MIN_DATE, next
            continue

        caption = post.caption or ""
        rows.append({
            "type": "caption",
            "source_type": source_type,
            "source_name": source_name,
            "post_shortcode": post.shortcode,
            "date": post_date.isoformat(),
            "text": caption,
            "mentions": extract_mentions(caption),
            "hashtags": extract_hashtags(caption),
            "likes": post.likes,
        })

        # ambil komentar (dibatasi)
        try:
            polite_delay()
            comment_count = 0
            for comment in post.get_comments():
                if comment_count >= MAX_COMMENTS_PER_POST:
                    break
                if len(rows) >= TARGET_TOTAL:
                    break
                rows.append({
                    "type": "comment",
                    "source_type": source_type,
                    "source_name": source_name,
                    "post_shortcode": post.shortcode,
                    "date": post_date.isoformat(),  # tanggal post; IG tidak selalu expose tanggal komentar individual
                    "text": comment.text,
                    "mentions": extract_mentions(comment.text),
                    "hashtags": extract_hashtags(comment.text),
                    "likes": None,
                })
                comment_count += 1
        except Exception as e:
            print(f"[WARN] Gagal ambil komentar post {post.shortcode}: {e}")

        count += 1
        print(f"[INFO] [{source_type}:{source_name}] post {count}/{max_posts} | total rows: {len(rows)}")
        polite_delay()

    return rows


def crawl_hashtag(L, hashtag: str, rows: list):
    print(f"\n[INFO] === Crawling hashtag #{hashtag} ===")
    try:
        h = instaloader.Hashtag.from_name(L.context, hashtag)
        crawl_posts_from_iterator(h.get_posts(), "hashtag", hashtag, rows, MAX_POSTS_PER_SOURCE)
    except Exception as e:
        print(f"[ERROR] Gagal crawl hashtag #{hashtag}: {e}")


def crawl_profile(L, username: str, source_type: str, rows: list):
    print(f"\n[INFO] === Crawling akun @{username} ({source_type}) ===")
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        if profile.is_private:
            print(f"[SKIP] Akun @{username} privat, dilewati.")
            return
        crawl_posts_from_iterator(profile.get_posts(), source_type, username, rows, MAX_POSTS_PER_SOURCE)
    except Exception as e:
        print(f"[ERROR] Gagal crawl akun @{username}: {e}")


# =========================================================
# 5. BANGUN GRAF INTERAKSI (mentions + co-hashtag)
# =========================================================
def build_interaction_graph(df: pd.DataFrame) -> nx.Graph:
    """
    Graf 1: source_name <-> akun yang di-mention (siapa nyebut siapa)
    Graf 2 (opsional terpisah): co-occurrence hashtag dalam post yang sama
    """
    G = nx.DiGraph()

    for _, row in df.iterrows():
        src = row["source_name"]
        G.add_node(src, node_type=row["source_type"])

        mentions = row["mentions"] if isinstance(row["mentions"], list) else eval(str(row["mentions"]))
        for mentioned in mentions:
            G.add_node(mentioned, node_type="mentioned_account")
            if G.has_edge(src, mentioned):
                G[src][mentioned]["weight"] += 1
            else:
                G.add_edge(src, mentioned, weight=1)

    return G


def build_hashtag_cooccurrence_graph(df: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()
    for _, row in df.iterrows():
        tags = row["hashtags"] if isinstance(row["hashtags"], list) else eval(str(row["hashtags"]))
        tags = list(set(tags))
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                a, b = tags[i], tags[j]
                if G.has_edge(a, b):
                    G[a][b]["weight"] += 1
                else:
                    G.add_edge(a, b, weight=1)
    return G


# =========================================================
# 6. MAIN
# =========================================================
def main():
    state = load_checkpoint()
    rows = []

    L = init_loader()

    all_sources = (
        [("hashtag", h) for h in HASHTAGS]
        + [("niche", a) for a in NICHE_ACCOUNTS]
        + [("actor", a) for a in ACTOR_ACCOUNTS]
    )

    for source_type, name in all_sources:
        source_key = f"{source_type}:{name}"
        if source_key in state["processed_sources"]:
            print(f"[SKIP] {source_key} sudah diproses sebelumnya (checkpoint).")
            continue

        if len(rows) >= TARGET_TOTAL:
            print("[INFO] Target tercapai, berhenti.")
            break

        if source_type == "hashtag":
            crawl_hashtag(L, name, rows)
        else:
            crawl_profile(L, name, source_type, rows)

        state["processed_sources"].append(source_key)
        state["rows_collected"] = len(rows)
        save_checkpoint(state)

        # simpan progress tiap sumber selesai, jaga-jaga kalau crash/di-block di tengah jalan
        if rows:
            pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False)
            print(f"[INFO] Checkpoint disimpan: {len(rows)} baris -> {OUTPUT_CSV}")

    # --- Simpan hasil akhir ---
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[DONE] Total {len(df)} baris tersimpan di {OUTPUT_CSV}")

    if len(df) > 0:
        # --- Bangun graf ---
        mention_graph = build_interaction_graph(df)
        hashtag_graph = build_hashtag_cooccurrence_graph(df)

        nx.write_gexf(mention_graph, OUTPUT_DIR / "graf_mentions.gexf")     # bisa dibuka di Gephi
        nx.write_gexf(hashtag_graph, OUTPUT_DIR / "graf_cohashtag.gexf")    # bisa dibuka di Gephi

        print(f"[DONE] Graf mentions: {mention_graph.number_of_nodes()} node, "
              f"{mention_graph.number_of_edges()} edge -> data/graf_mentions.gexf")
        print(f"[DONE] Graf co-hashtag: {hashtag_graph.number_of_nodes()} node, "
              f"{hashtag_graph.number_of_edges()} edge -> data/graf_cohashtag.gexf")
        print("[INFO] File .gexf bisa dibuka di Gephi (gratis) untuk visualisasi jaringan,")
        print("       sebagai pengganti NodeXL.")


if __name__ == "__main__":
    main()
