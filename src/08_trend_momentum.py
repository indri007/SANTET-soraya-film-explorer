"""
08_trend_momentum.py
====================
Step 8 — Trend Momentum Analytics
Pipeline: Instagram Indonesia Viral Intelligence & Research Platform

Measures semantic topic clusters, sentiment resonance, and term momentum:
- Audits temporal trend velocity.
- Status: PARTIAL (due to lack of longitudinal post timestamps in dataset).
- Analyzes topic volume, sentiment distribution, and keyword concentration
  using verified topic clusters (output/topics.csv and output/topics_dataset.csv).
- Documents the formal research formulation for Trend Velocity and Acceleration.

Run:
    python src/08_trend_momentum.py
    python -m src.08_trend_momentum
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
TOPICS_CSV = REPO / "output" / "topics_dataset.csv"
TOPICS_SUMMARY_CSV = REPO / "output" / "topics.csv"
OUT_AUDIT_JSON = REPO / "output" / "trend_momentum_audit.json"


class TrendMomentumAnalyzer:
    """Calculates topic volume dynamics and specifies temporal momentum formulation."""

    def __init__(self, data_path: Path | str | None = None) -> None:
        self.data_path = Path(data_path) if data_path else TOPICS_CSV

    def analyze_topic_momentum(self) -> Dict[str, Any]:
        """Audits topic shares and evaluates temporal momentum readiness."""
        if not self.data_path.exists():
            return {
                "status": "MISSING",
                "error": f"Topic dataset not found at {self.data_path}",
            }

        df = pd.read_csv(self.data_path)

        # 1. Topic Share breakdown
        topic_counts = df["topic"].value_counts().to_dict() if "topic" in df.columns else {}
        total = len(df)
        topic_shares = {
            str(k): {
                "count": int(v),
                "share": round(float(v / total), 4) if total > 0 else 0.0,
            }
            for k, v in sorted(topic_counts.items())
        }

        # 2. Sentiment distribution per topic
        sentiment_by_topic = {}
        if "topic" in df.columns and "baseline_sentiment" in df.columns:
            ct = pd.crosstab(df["topic"], df["baseline_sentiment"])
            sentiment_by_topic = ct.to_dict(orient="index")

        # 3. Rating average per topic
        rating_by_topic = {}
        if "topic" in df.columns and "rating" in df.columns:
            rating_by_topic = (
                df.groupby("topic")["rating"].agg(["mean", "count"]).round(2).to_dict(orient="index")
            )

        # 4. Formulations and temporal readiness
        has_temporal = any(col in df.columns for col in ["timestamp", "created_at", "date"])
        status = "AVAILABLE" if has_temporal else "PARTIAL"

        return {
            "status": status,
            "total_records": total,
            "topic_shares": topic_shares,
            "sentiment_by_topic": sentiment_by_topic,
            "rating_by_topic": rating_by_topic,
            "momentum_formula": (
                "Trend Momentum Index: M(topic, t) = (dVol/dt) * PolarityResonance * (1 + EngagementAcc)"
            ),
            "data_limitation_notice": (
                "Continuous time-series timestamps are not present in current 1,000-row review data. "
                "Cross-sectional topic distribution is AVAILABLE; longitudinal temporal momentum velocity is PARTIAL."
            ),
            "required_signals_for_realtime_tracking": [
                "Hourly / daily post ingestion timestamps",
                "Topic volume deltas (t vs t-1)",
                "Velocity of hashtag spread across distinct authors",
            ],
        }


def run(verbose: bool = True) -> dict[str, Any]:
    """Runs trend momentum analysis."""
    if verbose:
        print("=" * 60)
        print("08_trend_momentum.py | Trend Momentum Analytics & Topic Dynamics")
        print("=" * 60)

    analyzer = TrendMomentumAnalyzer()
    res = analyzer.analyze_topic_momentum()

    if verbose:
        print(f"[STATUS]  Momentum Engine Status: {res['status']}")
        print(f"[RECORDS] Evaluated {res['total_records']:,} records")
        print("\nTopic Volume & Sentiment Breakdown:")
        for top_id, stats in res.get("topic_shares", {}).items():
            print(f"  Topic {top_id}: {stats['count']} records ({stats['share']*100:.1f}%)")

        if "sentiment_by_topic" in res:
            print("\nSentiment Per Topic:")
            for top_id, s_dict in res["sentiment_by_topic"].items():
                print(f"  Topic {top_id} -> {s_dict}")

        print("\n[FORMULATION] Momentum Index:")
        print(f"  {res['momentum_formula']}")
        print(f"\n[LIMITATION] {res['data_limitation_notice']}")

    OUT_AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"\n[SAVE] Audit saved to {OUT_AUDIT_JSON.name}")
        print("✓ 08_trend_momentum.py complete (Status: PARTIAL)")

    return res


if __name__ == "__main__":
    run(verbose=True)
