import re, time, random, json, logging
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd, networkx as nx, instaloader

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

# === KONFIGURASI ===
IG_USERNAME = "indrikartika444"
HASHTAGS = [
    "indonesia", "viral", "trending", "fyp", "beranda",
    "exploreindonesia", "indonesiaku", "nusantara",
    "politikindonesia", "pemilu", "umkm", "bisnisonline",
    "budayaindonesia", "kuliner", "musik", "film",
    "lingkungan", "pendidikan", "kesehatan", "covid19",
]
MIN_FOLLOWERS  = 100
TARGET_ROWS    = 10000
MAX_POSTS      = 200
MAX_COMMENTS   = 20
MIN_DATE       = datetime(2020, 1, 1, tzinfo=timezone.utc)
DELAY_MIN, DELAY_MAX = 4, 9

ID_KEYWORDS = ["indonesia","indo","jakarta","bandung","surabaya",
               "medan","bali","yogyakarta","makassar","semarang",
               "palembang","bogor","wib","wita","depok","bekasi"]

OUT = Path("data"); OUT.mkdir(exist_ok=True)
CSV_ALL    = OUT / "instagram_indonesia_all.csv"
CKPT       = OUT / "crawl_checkpoint.json"

def init_loader():
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True
    )

    if not IG_USERNAME:
        log.warning("Berjalan TANPA login - rate limit lebih ketat")
        return L

    try:
        session_file = Path.home() / ".config" / "instaloader" / f"session-{IG_USERNAME}"
        L.load_session_from_file(IG_USERNAME, filename=str(session_file))
        log.info("SESSION_VERIFIED")
        return L

    except FileNotFoundError:
        log.error("SESSION_NOT_FOUND")
        log.error("Instagram session belum tersedia.")
        log.error("Crawler dihentikan sebelum pengambilan data.")
        raise RuntimeError(
            "INSTAGRAM_SESSION_NOT_FOUND: buat session Instagram terlebih dahulu."
        )

    except Exception as exc:
        log.error("SESSION_LOAD_FAILED: %s", type(exc).__name__)
        raise RuntimeError(
            "INSTAGRAM_SESSION_INVALID_OR_UNAVAILABLE"
        ) from exc

def delay(f=1.0): time.sleep(random.uniform(DELAY_MIN, DELAY_MAX) * f)

def is_indonesia(profile):
    if profile.followers < MIN_FOLLOWERS or profile.is_private: return False
    txt = " ".join([profile.username.lower(),
                    (profile.full_name or "").lower(),
                    (profile.biography or "").lower()])
    return any(k in txt for k in ID_KEYWORDS)

def mentions(t): return re.findall(r"@(\w+)", t or "")
def hashtags(t): return re.findall(r"#(\w+)", t or "")

def mkrow(ptype, src_type, src_name, code, dt, text, likes, uname, followers):
    return {"type":ptype,"source_type":src_type,"source_name":src_name,
            "post_shortcode":code,"year":dt.year,
            "month":f"{dt.year}-{dt.month:02d}","date":dt.isoformat(),
            "text":text,
            "mentions":json.dumps(mentions(text), ensure_ascii=False),
            "hashtags":json.dumps(hashtags(text), ensure_ascii=False),
            "likes":likes,"poster_username":uname,"poster_followers":followers}

def load_ckpt():
    if CKPT.exists():
        with open(CKPT) as f:
            return json.load(f)
    return {"done": [], "rows": 0, "accounts": []}

def save_ckpt(state):
    with open(CKPT, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_existing_rows():
    if not CSV_ALL.exists():
        return []

    try:
        df = pd.read_csv(CSV_ALL)

        if df.empty:
            return []

        rows = df.to_dict("records")
        log.info(f"RESUME: loaded {len(rows)} existing rows from {CSV_ALL}")
        return rows

    except Exception as e:
        log.warning(f"Gagal membaca CSV lama: {e}")
        return []

def is_rate_limit_error(exc):
    msg = str(exc).lower()

    patterns = [
        "please wait a few minutes",
        "401 unauthorized",
        "429",
        "too many requests",
        "rate limit",
        "checkpoint required",
        "login required",
    ]

    return any(p in msg for p in patterns)

def retry_delay(attempt):
    base = 30 * (2 ** attempt)
    jitter = random.uniform(0, 10)
    return min(base + jitter, 600)

def crawl_post(post, src_type, src_name, rows, accounts):
    dt = post.date_utc.replace(tzinfo=timezone.utc)

    if dt < MIN_DATE or len(rows) >= TARGET_ROWS:
        return

    uname = post.owner_username

    try:
        flw = post.owner_profile.followers
        private = post.owner_profile.is_private
    except Exception:
        flw = None
        private = False

    # Filter akun
    if private:
        return

    if flw is not None and flw < MIN_FOLLOWERS:
        return

    cap = post.caption or ""

    if cap.strip():
        rows.append(
            mkrow(
                "caption",
                src_type,
                src_name,
                post.shortcode,
                dt,
                cap,
                post.likes,
                uname,
                flw
            )
        )

    accounts.add(uname)

    if len(rows) < TARGET_ROWS:
        attempt = 0

        while attempt < 4:
            try:
                delay(0.4)
                n = 0

                for c in post.get_comments():
                    if n >= MAX_COMMENTS or len(rows) >= TARGET_ROWS:
                        break

                    if c.text and c.text.strip():
                        cu = c.owner.username if c.owner else ""

                        rows.append(
                            mkrow(
                                "comment",
                                src_type,
                                src_name,
                                post.shortcode,
                                dt,
                                c.text,
                                None,
                                cu,
                                None
                            )
                        )

                        if cu:
                            accounts.add(cu)

                        n += 1

                break

            except Exception as e:
                if is_rate_limit_error(e) and attempt < 3:
                    wait_time = retry_delay(attempt)

                    log.warning(
                        f"Rate limit komentar {post.shortcode}; "
                        f"retry {attempt + 1}/3 dalam {wait_time:.1f} detik"
                    )

                    time.sleep(wait_time)
                    attempt += 1

                else:
                    log.warning(
                        f"Komentar {post.shortcode} gagal: {e}"
                    )
                    break

def crawl_hashtag(L, tag, rows, accounts):
    log.info(f">>> #{tag} | rows so far: {len(rows)}")
    try:
        h = instaloader.Hashtag.from_name(L.context, tag)
        n=0
        for post in h.get_posts():
            if n>=MAX_POSTS or len(rows)>=TARGET_ROWS: break
            crawl_post(post,"hashtag",tag,rows,accounts)
            n+=1
            if n%10==0: log.info(f"  #{tag}: {n} posts | total: {len(rows)} rows")
            delay()
    except Exception as e: log.error(f"Gagal #{tag}: {e}")

def save_csv(rows):
    if rows:
        pd.DataFrame(rows).to_csv(CSV_ALL,index=False)
        log.info(f"  Saved: {len(rows)} rows -> {CSV_ALL}")

def build_graphs(df):
    Gm=nx.DiGraph(); Gh=nx.Graph()
    for _,r in df[df["type"]=="caption"].iterrows():
        src=r["poster_username"]
        for m in json.loads(r["mentions"]):
            if Gm.has_edge(src,m): Gm[src][m]["weight"]+=1
            else: Gm.add_edge(src,m,weight=1)
        tags=list(set(json.loads(r["hashtags"])))
        for i in range(len(tags)):
            for j in range(i+1,len(tags)):
                a,b=tags[i].lower(),tags[j].lower()
                if Gh.has_edge(a,b): Gh[a][b]["weight"]+=1
                else: Gh.add_edge(a,b,weight=1)
    nx.write_gexf(Gm, OUT/"graf_mentions.gexf")
    nx.write_gexf(Gh, OUT/"graf_cohashtag.gexf")
    log.info(f"Graf mentions: {Gm.number_of_nodes()} nodes {Gm.number_of_edges()} edges")
    log.info(f"Graf co-hashtag: {Gh.number_of_nodes()} nodes {Gh.number_of_edges()} edges")

def main():
    log.info("=" * 55)
    log.info(f"Instagram Indonesia Crawler")
    log.info(f"Target: {TARGET_ROWS} rows | Min followers: {MIN_FOLLOWERS}")
    log.info("=" * 55)
    state = load_ckpt()

    # Resume existing dataset
    rows = load_existing_rows()

    # Safety limit
    if len(rows) > TARGET_ROWS:
        rows = rows[:TARGET_ROWS]

    accounts = set(state.get("accounts", []))

    # Recover accounts from existing data
    for r in rows:
        uname = r.get("poster_username")
        if uname and str(uname) != "nan":
            accounts.add(str(uname))

    done = set(state.get("done", []))

    log.info(f"RESUME ROWS: {len(rows)}")
    log.info(f"DONE HASHTAGS: {len(done)}")

    if len(rows) >= TARGET_ROWS:
        log.info("TARGET_ROWS SUDAH TERCAPAI")
        return

    L = init_loader()
    for tag in HASHTAGS:
        key=f"hashtag:{tag}"
        if key in done:
            log.info(f"SKIP #{tag} (sudah diproses)"); continue
        if len(rows)>=TARGET_ROWS: break
        crawl_hashtag(L,tag,rows,accounts)
        done.add(key)
        state.update({"done":list(done),"rows":len(rows),"accounts":list(accounts)})
        save_ckpt(state); save_csv(rows)
    df=pd.DataFrame(rows)
    if len(df)==0:
        log.warning("Tidak ada data."); return
    df.to_csv(CSV_ALL,index=False)
    log.info(f"SELESAI: {len(df)} baris")
    log.info(df.groupby("year").size().to_string())
    per_yr=OUT/"per_tahun"; per_yr.mkdir(exist_ok=True)
    for yr,g in df.groupby("year"): g.to_csv(per_yr/f"data_{yr}.csv",index=False)
    build_graphs(df)

if __name__=="__main__": main()
