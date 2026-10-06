#!/usr/bin/env python3
"""
soraya_db.py — Database schema & ORM layer for Soraya Film Explorer
Implements PRD Section 8 ERD schema.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "soraya_explorer.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. films table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS films (
        film_id TEXT PRIMARY KEY,
        judul TEXT NOT NULL,
        judul_en TEXT,
        rumah_produksi TEXT NOT NULL,
        tanggal_rilis TEXT NOT NULL,
        tahun INTEGER NOT NULL,
        genre TEXT NOT NULL,
        sutradara TEXT,
        pemain_utama TEXT,
        is_franchise INTEGER DEFAULT 0,
        momen_rilis TEXT,
        tanggal_streaming TEXT,
        platform_streaming TEXT,
        status_produksi TEXT DEFAULT 'Released',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. box_office table (Multi-source provenance)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS box_office (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        film_id TEXT NOT NULL,
        source TEXT NOT NULL,
        retrieved_at TEXT NOT NULL,
        penonton INTEGER NOT NULL,
        hari_ke INTEGER,
        is_final INTEGER DEFAULT 0,
        is_official_selected INTEGER DEFAULT 0,
        source_url TEXT,
        catatan TEXT,
        FOREIGN KEY (film_id) REFERENCES films(film_id)
    );
    """)

    # 3. trends_daily table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trends_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        film_id TEXT NOT NULL,
        keyword TEXT NOT NULL,
        property TEXT DEFAULT 'web', -- 'web' or 'youtube'
        tanggal TEXT NOT NULL,
        skor REAL NOT NULL,
        skor_normalisasi REAL,
        anchor_keyword TEXT DEFAULT 'suzzanna',
        retrieved_at TEXT,
        FOREIGN KEY (film_id) REFERENCES films(film_id)
    );
    """)

    # 4. trends_region table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trends_region (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        film_id TEXT NOT NULL,
        keyword TEXT NOT NULL,
        provinsi TEXT NOT NULL,
        skor REAL NOT NULL,
        rentang_tanggal TEXT,
        FOREIGN KEY (film_id) REFERENCES films(film_id)
    );
    """)

    # 5. yt_videos table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS yt_videos (
        video_id TEXT PRIMARY KEY,
        film_id TEXT NOT NULL,
        jenis TEXT NOT NULL, -- 'trailer', 'teaser', 'bts', 'ost'
        judul_video TEXT NOT NULL,
        channel_id TEXT NOT NULL,
        channel_title TEXT,
        published_at TEXT NOT NULL,
        durasi TEXT,
        video_url TEXT,
        FOREIGN KEY (film_id) REFERENCES films(film_id)
    );
    """)

    # 6. yt_snapshots table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS yt_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id TEXT NOT NULL,
        captured_at TEXT NOT NULL,
        days_relative_to_release INTEGER, -- H-X or H+X
        views INTEGER NOT NULL,
        likes INTEGER NOT NULL,
        comments INTEGER NOT NULL,
        FOREIGN KEY (video_id) REFERENCES yt_videos(video_id)
    );
    """)

    # 7. yt_comments table (anonymized hash according to PDP Law)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS yt_comments (
        comment_id TEXT PRIMARY KEY,
        video_id TEXT NOT NULL,
        author_hash TEXT NOT NULL,
        teks TEXT NOT NULL,
        likes INTEGER DEFAULT 0,
        published_at TEXT,
        sentimen TEXT, -- 'positive', 'neutral', 'negative'
        sentiment_score REAL, -- [-1.0, 1.0]
        contains_intent_to_watch INTEGER DEFAULT 0,
        FOREIGN KEY (video_id) REFERENCES yt_videos(video_id)
    );
    """)

    # 8. support_metrics table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS support_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        film_id TEXT NOT NULL,
        source TEXT NOT NULL, -- 'IMDb', 'Letterboxd', 'Netflix', 'TikTok'
        metric TEXT NOT NULL, -- 'rating', 'votes', 'weeks_in_top10', 'hashtag_views'
        tanggal TEXT,
        nilai REAL NOT NULL,
        detail TEXT,
        FOREIGN KEY (film_id) REFERENCES films(film_id)
    );
    """)

    # 9. pipeline_logs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_name TEXT NOT NULL,
        status TEXT NOT NULL,
        records_affected INTEGER,
        log_message TEXT,
        executed_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"Database initialized successfully at: {DB_PATH}")
