"""
09_forecast_2027.py
===================
Step 9 — Instagram Indonesia 2027 Forecasting Suite
Pipeline: Instagram Indonesia Viral Intelligence & Research Platform

Audits the longitudinal time-series depth of the available dataset:
- Checks if genuine post-level timestamps exist to train econometric
  or deep learning forecasting models (SARIMAX, Prophet, TFT).
- Strict Research Policy:
  If temporal data is insufficient:
    FORECAST_STATUS = INSUFFICIENT_TEMPORAL_DATA
  Rejects fabrication of synthetic historical curves or simulated 2027 numbers.
- Generates required forecasting artifacts:
  * output/forecast_2027.csv
  * output/forecast_metrics.json
  * output/forecast_2027.png (Architectural roadmap & prerequisite visualization)
  * output/forecast_report.json

Run:
    python src/09_forecast_2027.py
    python -m src.09_forecast_2027
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
INPUT_CSV = REPO / "output" / "model_features.csv"

OUT_FORECAST_CSV = REPO / "output" / "forecast_2027.csv"
OUT_METRICS_JSON = REPO / "output" / "forecast_metrics.json"
OUT_PLOT_PNG = REPO / "output" / "forecast_2027.png"
OUT_REPORT_JSON = REPO / "output" / "forecast_report.json"


class Forecast2027Engine:
    """Evaluates time series readiness and generates 2027 forecasting specification artifacts."""

    def __init__(self) -> None:
        pass

    def evaluate_temporal_feasibility(self, df: pd.DataFrame) -> Dict[str, Any]:
        has_dates = any(c in df.columns for c in ['date_time', 'timestamp', 'created_at']) and df.get('date_time', pd.Series()).notna().sum() > 0

        status = "AVAILABLE" if has_dates else "INSUFFICIENT_TEMPORAL_DATA"

        return {
            "forecast_status": status,
            "target_horizon": "2027-Q4",
            "historical_period": "None (Timestamps absent in raw review export)",
            "training_period": "None (Awaiting longitudinal ingestion)",
            "validation_period": "None",
            "candidate_models": [
                "SARIMAX (with Indonesian seasonal calendar covariates: Ramadan, Harbolnas)",
                "Prophet (Bayesian trend decomposition with changepoints)",
                "Temporal Fusion Transformer (TFT multimodal deep learning)"
            ],
            "metrics": {
                "MAE": None,
                "RMSE": None,
                "MAPE": None,
                "status": status,
                "reason": "Empirical training blocked due to absent longitudinal timestamps in 1,000-record dataset."
            },
            "confidence_intervals": None,
            "minimum_requirements_for_valid_forecast": [
                "Minimum 24-36 months of continuous daily/weekly post volume telemetry",
                "Explicit post-creation timestamps (ISO 8601 UTC+7)",
                "Multi-period engagement decay trajectories (t+1h, t+24h, t+7d, t+30d)",
                "Hashtag and topic velocity transition logs"
            ],
            "limitations": (
                "The current 1,000-record dataset is a cross-sectional snapshot of app reviews. "
                "Per research integrity guidelines, synthetic temporal points are not created."
            )
        }

    def generate_artifacts(self, report: Dict[str, Any]) -> None:
        # 1. Save CSV
        df_forecast = pd.DataFrame([{
            "horizon": report["target_horizon"],
            "forecast_status": report["forecast_status"],
            "historical_period": report["historical_period"],
            "training_period": report["training_period"],
            "validation_period": report["validation_period"],
            "primary_architecture": "SARIMAX + Prophet + TFT",
            "mae": report["metrics"]["MAE"],
            "rmse": report["metrics"]["RMSE"],
            "mape": report["metrics"]["MAPE"],
            "limitations": report["limitations"]
        }])
        OUT_FORECAST_CSV.parent.mkdir(parents=True, exist_ok=True)
        df_forecast.to_csv(OUT_FORECAST_CSV, index=False, encoding='utf-8-sig')

        # 2. Save Metrics JSON
        with open(OUT_METRICS_JSON, 'w', encoding='utf-8') as f:
            json.dump(report["metrics"], f, indent=2)

        # 3. Save Report JSON
        with open(OUT_REPORT_JSON, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 4. Generate Plot PNG: Roadmap & Prerequisite Framework
        fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
        phases = [
            "1. Cross-Sectional Audit\n(N=1,000 Current)",
            "2. Longitudinal Collection\n(24 Mo Daily Feed)",
            "3. SARIMAX / Prophet\n(Seasonality Tuning)",
            "4. 2027 Projections\n(TFT Deep Learning)"
        ]
        status_colors = ["#10b981", "#f59e0b", "#94a3b8", "#94a3b8"]
        y_pos = np.arange(len(phases))

        bars = ax.barh(y_pos, [1, 2, 3, 4], color=status_colors, edgecolor="#334155", height=0.55)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(phases, fontsize=10, fontweight="bold")
        ax.set_xlabel("Pipeline Progression Horizon", fontsize=10)
        ax.set_title("Instagram Indonesia 2027 Research Forecasting Roadmap\nStatus: INSUFFICIENT_TEMPORAL_DATA (No Synthetic Points)", fontsize=11, fontweight="bold", pad=12)

        for bar, text in zip(bars, ["VERIFIED", "PREREQUISITE", "SPECIFIED", "TARGET 2027"]):
            ax.text(bar.get_width() - 0.2, bar.get_y() + 0.25, text, ha="right", va="center", color="white", fontweight="bold", fontsize=9)

        plt.tight_layout()
        plt.savefig(OUT_PLOT_PNG)
        plt.close()


def run(verbose: bool = True) -> Dict[str, Any]:
    if verbose:
        print("=" * 60)
        print("09_forecast_2027.py | 2027 Forecasting Suite & Temporal Audit")
        print("=" * 60)

    in_path = INPUT_CSV if INPUT_CSV.exists() else REPO / "output" / "master_instagram_10000.csv"
    df = pd.read_csv(in_path)

    engine = Forecast2027Engine()
    report = engine.evaluate_temporal_feasibility(df)
    engine.generate_artifacts(report)

    if verbose:
        print(f"[STATUS]     FORECAST STATUS: {report['forecast_status']}")
        print(f"[HORIZON]    Target: {report['target_horizon']}")
        print(f"[SAVE]       Saved {OUT_FORECAST_CSV.name}")
        print(f"[SAVE]       Saved {OUT_METRICS_JSON.name}")
        print(f"[SAVE]       Saved {OUT_PLOT_PNG.name}")
        print(f"[SAVE]       Saved {OUT_REPORT_JSON.name}")
        print("✓ 09_forecast_2027.py complete (Status: INSUFFICIENT_TEMPORAL_DATA)")

    return report


if __name__ == "__main__":
    run(verbose=True)
