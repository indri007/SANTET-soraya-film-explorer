"""
02_viral_score.py
=================
Step 2 — Viral Intelligence Engine & Empirical Engagement Audit
Pipeline: Instagram Indonesia Viral Intelligence & Research Platform

Audits the availability of genuine Instagram interaction metrics
(likes, comments, shares, saves, impressions, views).

Strict Research Policy:
- If native post interaction telemetry is absent:
    VIRAL_SCORE_STATUS = INSUFFICIENT_ENGAGEMENT_DATA
- Prohibits fabrication of artificial engagement counts.
- Documents mathematical formulation for empirical viral score calculation.
- Computes Content Virality Propensity Proxy (CVPP) based purely on
  content structure (hashtags, mentions, emojis, text length).

Outputs:
  output/viral_scores.csv
  output/viral_score_report.json

Run:
    python src/02_viral_score.py
    python -m src.02_viral_score
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
INPUT_CSV = REPO / "output" / "model_features.csv"
FALLBACK_CSV = REPO / "output" / "master_instagram_10000.csv"

OUT_SCORES_CSV = REPO / "output" / "viral_scores.csv"
OUT_REPORT_JSON = REPO / "output" / "viral_score_report.json"

REQUIRED_ENGAGEMENT_METRICS = [
    "likes",
    "comments",
    "shares",
    "saves",
    "views",
    "impressions",
    "reach",
    "follower_count"
]


class ViralScoreEngine:
    """Evaluates viral engagement feasibility and calculates structural content proxy."""

    def __init__(self) -> None:
        pass

    def evaluate_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        present = [m for m in REQUIRED_ENGAGEMENT_METRICS if m in df.columns and df[m].notna().sum() > 0]
        missing = [m for m in REQUIRED_ENGAGEMENT_METRICS if m not in present]

        has_sufficient_engagement = len(present) >= 3
        status = "AVAILABLE" if has_sufficient_engagement else "INSUFFICIENT_ENGAGEMENT_DATA"

        return {
            "viral_score_status": status,
            "required_metrics": REQUIRED_ENGAGEMENT_METRICS,
            "present_metrics": present,
            "missing_metrics": missing,
            "engagement_coverage": round(len(present) / len(REQUIRED_ENGAGEMENT_METRICS), 4),
            "empirical_viral_score_available": has_sufficient_engagement,
            "formula_specification": (
                "Empirical Viral Score (VS): "
                "VS = w1*(likes/reach) + 2.5*w2*(shares/reach) + 2.0*w3*(saves/reach) + 1.5*w4*(comments/reach) * decay_factor"
            ),
            "structural_proxy_specification": (
                "Content Virality Propensity Proxy (CVPP): "
                "0.35*norm(hashtag_count) + 0.25*norm(mention_count) + 0.20*norm(emoji_count) + 0.20*norm(text_length)"
            ),
            "scientific_limitation_notice": (
                "The current 1,000-record dataset originates from app store consumer reviews, which do not contain "
                "post-level Instagram interaction telemetry (likes, comments, shares, views). "
                "An empirical viral score CANNOT be claimed without true interaction logs."
            )
        }

    def compute_scores_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()

        text_len = out['text_length'].fillna(0).astype(float) if 'text_length' in out.columns else out['original_text'].astype(str).str.len()
        hashtags = out['hashtag_count'].fillna(0).astype(float) if 'hashtag_count' in out.columns else 0.0
        mentions = out['mention_count'].fillna(0).astype(float) if 'mention_count' in out.columns else 0.0
        emojis = out['emoji_count'].fillna(0).astype(float) if 'emoji_count' in out.columns else 0.0

        # Structural proxy CVPP (0 to 1)
        norm_len = np.clip(text_len / 500.0, 0, 1)
        norm_hash = np.clip(hashtags / 5.0, 0, 1)
        norm_ment = np.clip(mentions / 5.0, 0, 1)
        norm_emoj = np.clip(emojis / 5.0, 0, 1)

        out['content_virality_proxy_cvpp'] = (0.35 * norm_hash + 0.25 * norm_ment + 0.20 * norm_emoj + 0.20 * norm_len).round(4)
        out['empirical_viral_score'] = pd.NA
        out['viral_score_status'] = 'INSUFFICIENT_ENGAGEMENT_DATA'

        cols_to_save = ['record_id', 'username', 'rating', 'content_virality_proxy_cvpp', 'empirical_viral_score', 'viral_score_status']
        avail_cols = [c for c in cols_to_save if c in out.columns]
        return out[avail_cols]


def run(verbose: bool = True) -> Dict[str, Any]:
    if verbose:
        print("=" * 60)
        print("02_viral_score.py | Viral Score Engine & Engagement Audit")
        print("=" * 60)

    in_path = INPUT_CSV if INPUT_CSV.exists() else FALLBACK_CSV
    df = pd.read_csv(in_path)

    engine = ViralScoreEngine()
    audit = engine.evaluate_features(df)
    scores_df = engine.compute_scores_dataframe(df)

    # Save outputs
    OUT_SCORES_CSV.parent.mkdir(parents=True, exist_ok=True)
    scores_df.to_csv(OUT_SCORES_CSV, index=False, encoding='utf-8-sig')

    with open(OUT_REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"[STATUS]     Viral Score Status: {audit['viral_score_status']}")
        print(f"[COVERAGE]   Engagement Coverage: {audit['engagement_coverage']*100:.1f}%")
        print(f"[MISSING]    Missing Metrics: {audit['missing_metrics']}")
        print(f"[SAVE]       Saved {OUT_SCORES_CSV.name} ({len(scores_df)} rows)")
        print(f"[SAVE]       Saved {OUT_REPORT_JSON.name}")
        print("✓ 02_viral_score.py complete (Status: INSUFFICIENT_ENGAGEMENT_DATA)")

    return audit


if __name__ == "__main__":
    run(verbose=True)
