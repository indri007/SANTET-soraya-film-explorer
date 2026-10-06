"""
04_feature_engineering.py
=========================
Step 4 — Unified Feature Engineering Suite
Pipeline: Instagram Indonesia Viral Intelligence & Research Platform

Merges:
1. Master dataset (output/master_instagram_10000.csv)
2. IndoBERT features (output/indobert_features.csv)
   - indobert_sentiment, sentiment_confidence, probabilities, emotion
3. Topic clusters (output/topics_dataset.csv)
4. Stylistic & structural indicators:
   - text_length, token_count, char_count, word_count, avg_word_length
   - hashtag_count, mention_count, emoji_count, url_count
   - uppercase_count, uppercase_ratio, lexical_diversity
5. Explicit metadata columns for temporal (day, week, month, year)
   and engagement (likes, comments, shares).

Output:
  output/model_features.csv
  output/features_audit.json

Run:
    python src/04_feature_engineering.py
    python -m src.04_feature_engineering
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
MASTER_CSV = REPO / "output" / "master_instagram_10000.csv"
FALLBACK_MASTER = REPO / "data" / "Review Instagram.csv"
INDOBERT_CSV = REPO / "output" / "indobert_features.csv"
TOPICS_CSV = REPO / "output" / "topics_dataset.csv"

OUT_MODEL_FEATURES_CSV = REPO / "output" / "model_features.csv"
OUT_AUDIT_JSON = REPO / "output" / "features_audit.json"


def count_emojis(text: str) -> int:
    import unicodedata
    return sum(1 for ch in str(text) if "EMOJI" in unicodedata.name(ch, "") or unicodedata.category(ch) in ["So", "Sk"])


def extract_features(df_master: pd.DataFrame) -> pd.DataFrame:
    df = df_master.copy()
    texts = df['original_text'].fillna('').astype(str)

    # 1. Structural features
    df['char_count'] = texts.str.len()
    df['text_length'] = df['char_count']
    df['word_count'] = texts.apply(lambda s: len(s.split()))
    df['token_count'] = df['word_count']
    df['avg_word_length'] = np.where(df['word_count'] > 0, df['char_count'] / df['word_count'], 0).round(2)

    # 2. Social cues
    _RE_URL = re.compile(r'https?://\S+|www\.\S+', re.IGNORECASE)
    _RE_MENTION = re.compile(r'@\w+')
    _RE_HASHTAG = re.compile(r'#\w+')

    df['url_count'] = texts.apply(lambda s: len(_RE_URL.findall(s)))
    df['mention_count'] = texts.apply(lambda s: len(_RE_MENTION.findall(s)))
    df['hashtag_count'] = texts.apply(lambda s: len(_RE_HASHTAG.findall(s)))
    df['emoji_count'] = texts.apply(count_emojis)

    # 3. Stylistic & expressiveness
    df['uppercase_count'] = texts.apply(lambda s: sum(1 for c in s if c.isupper()))
    df['uppercase_ratio'] = np.where(df['char_count'] > 0, (df['uppercase_count'] / df['char_count']).round(4), 0.0)
    df['exclamation_count'] = texts.str.count(r'!')
    df['question_count'] = texts.str.count(r'\?')
    df['digit_count'] = texts.str.count(r'\d')

    def calc_ttr(s: str) -> float:
        words = s.lower().split()
        return round(len(set(words)) / len(words), 4) if words else 0.0
    df['lexical_diversity'] = texts.apply(calc_ttr)

    # 4. Temporal columns (Audited: Absent in raw review export)
    df['day'] = pd.NA
    df['week'] = pd.NA
    df['month'] = pd.NA
    df['year'] = pd.NA
    df['temporal_status'] = 'INSUFFICIENT_TEMPORAL_DATA'

    # 5. Engagement columns (Audited: Absent in raw review export)
    df['engagement_likes'] = pd.NA
    df['engagement_comments'] = pd.NA
    df['engagement_shares'] = pd.NA
    df['engagement_views'] = pd.NA
    df['engagement_status'] = 'INSUFFICIENT_ENGAGEMENT_DATA'

    return df


def run(verbose: bool = True) -> Dict[str, Any]:
    if verbose:
        print("=" * 60)
        print("04_feature_engineering.py | Unified Feature Engineering")
        print("=" * 60)

    # 1. Load Master Dataset
    master_path = MASTER_CSV if MASTER_CSV.exists() else FALLBACK_MASTER
    df_m = pd.read_csv(master_path)
    if 'original_text' not in df_m.columns and 'Review Text' in df_m.columns:
        df_m = df_m.rename(columns={'Review Text': 'original_text', 'UserName': 'username', 'Rating': 'rating'})
    if 'record_id' not in df_m.columns:
        df_m['record_id'] = [f'IG-{i+1:06d}' for i in range(len(df_m))]

    # 2. Extract structural & linguistic features
    df_feat = extract_features(df_m)

    # 3. Merge IndoBERT features
    if INDOBERT_CSV.exists():
        df_bert = pd.read_csv(INDOBERT_CSV)
        bert_cols = ['record_id', 'indobert_sentiment', 'sentiment_confidence', 'prob_positive', 'prob_neutral', 'prob_negative', 'emotion']
        available_bert_cols = [c for c in bert_cols if c in df_bert.columns]
        df_feat = df_feat.merge(df_bert[available_bert_cols], on='record_id', how='left')
        indobert_status = 'AVAILABLE'
    else:
        df_feat['indobert_sentiment'] = 'neutral'
        df_feat['emotion'] = 'neutral'
        indobert_status = 'MISSING'

    # 4. Merge Topics
    if TOPICS_CSV.exists():
        df_top = pd.read_csv(TOPICS_CSV)
        if 'topic' in df_top.columns and len(df_top) == len(df_feat):
            df_feat['topic'] = df_top['topic'].values
        else:
            df_feat['topic'] = 0
    else:
        df_feat['topic'] = 0

    # 5. Save output
    OUT_MODEL_FEATURES_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_feat.to_csv(OUT_MODEL_FEATURES_CSV, index=False, encoding='utf-8-sig')

    audit = {
        'status': 'AVAILABLE',
        'records_engineered': len(df_feat),
        'total_feature_columns': len(df_feat.columns),
        'indobert_integration': indobert_status,
        'feature_list': list(df_feat.columns),
        'sentiment_distribution': df_feat['indobert_sentiment'].value_counts().to_dict() if 'indobert_sentiment' in df_feat.columns else {},
        'emotion_distribution': df_feat['emotion'].value_counts().to_dict() if 'emotion' in df_feat.columns else {},
        'output_file': str(OUT_MODEL_FEATURES_CSV),
    }

    with open(OUT_AUDIT_JSON, 'w', encoding='utf-8') as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"[SAVE]  Model features saved: {OUT_MODEL_FEATURES_CSV.name} ({len(df_feat)} rows, {len(df_feat.columns)} cols)")
        print(f"[AUDIT] Features audit saved to {OUT_AUDIT_JSON.name}")
        print("✓ 04_feature_engineering.py complete")

    return audit


if __name__ == "__main__":
    run(verbose=True)
