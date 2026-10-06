#!/usr/bin/env python3
"""
generate_nodexl_10m.py
Generator Streaming Dataset 10.000.000 Interaksi NodeXL Instagram Indonesia (2020-2026)
Mencakup: Reel, Story, Like, Share, Komen, dan Live.
Dipartisi ke dalam 10 chunk x 1.000.000 relasi (terkompresi GZIP) agar ramah memori & Git.
"""

import gzip
import csv
import os
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output" / "nodexl_10m_chunks"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FORMAT_WEIGHTS = [
    ("reel", 0.42),
    ("story", 0.28),
    ("like", 0.14),
    ("komen", 0.08),
    ("share", 0.06),
    ("live", 0.02)
]

TOPICS = ["General_Lifestyle", "Technology", "Culinary", "Fashion_Beauty", "Travel_Lifestyle", "Comedy_Entertainment", "Business_Finance"]
SENTIMENTS = ["neutral", "positive", "negative"]

def generate_chunk(chunk_idx: int, records_per_chunk: int = 1000000):
    chunk_file = OUTPUT_DIR / f"nodexl_edges_chunk_{chunk_idx:02d}.csv.gz"
    print(f"[CHUNK {chunk_idx:02d}/10] Menulis {records_per_chunk:,} relasi ke {chunk_file.name}...")
    
    with gzip.open(chunk_file, "wt", newline="", encoding="utf-8") as gz:
        writer = csv.DictWriter(gz, fieldnames=[
            "vertex_1", "vertex_2", "format_modality", "interaction_type",
            "weight", "relationship_date", "year", "sentiment", "topic"
        ])
        writer.writeheader()
        
        for i in range(records_per_chunk):
            r = random.random()
            cum = 0
            fmt = "reel"
            for f_name, f_weight in FORMAT_WEIGHTS:
                cum += f_weight
                if r <= cum:
                    fmt = f_name
                    break
                    
            user_id = f"user_{random.randint(1, 50000)}"
            target_id = f"#trend_{random.randint(1, 5000)}"
            yr = random.randint(2020, 2026)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            date_str = f"{yr}-{month:02d}-{day:02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:00"
            
            # Formulate interaction weight
            if fmt == "reel":
                weight = random.randint(50, 50000)
                action = "play_and_watch"
            elif fmt == "story":
                weight = random.randint(10, 15000)
                action = "tap_impression"
            elif fmt == "like":
                weight = random.randint(1, 5000)
                action = "heart_reaction"
            elif fmt == "komen":
                weight = random.randint(1, 1200)
                action = "text_comment"
            elif fmt == "share":
                weight = random.randint(1, 800)
                action = "dm_share"
            else: # live
                weight = random.randint(100, 25000)
                action = "live_viewers"
                
            writer.writerow({
                "vertex_1": user_id,
                "vertex_2": target_id,
                "format_modality": fmt,
                "interaction_type": action,
                "weight": weight,
                "relationship_date": date_str,
                "year": yr,
                "sentiment": random.choices(SENTIMENTS, weights=[0.80, 0.18, 0.02])[0],
                "topic": random.choice(TOPICS)
            })
            
    sz_mb = os.path.getsize(chunk_file) / (1024 * 1024)
    print(f"✓ Selesai Chunk {chunk_idx:02d}: {sz_mb:.2f} MB")
    return chunk_file

if __name__ == "__main__":
    print("=" * 65)
    print("   GENERATOR DATASET 10.000.000 INTERAKSI INSTAGRAM NODEXL")
    print("=" * 65)
    print("Mencakup: Reel (42%), Story (28%), Like (14%), Komen (8%), Share (6%), Live (2%)")
    # Generate initial benchmark chunk
    generate_chunk(1, records_per_chunk=100000)
    print("\nUntuk mengenerate keseluruhan 10 chunk penuh, panggil: [generate_chunk(i) for i in range(1, 11)]")
