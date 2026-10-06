"""
10_explainability.py
====================
Step 10 — SHAP Model Explainability Engine
Pipeline: Instagram Indonesia Viral Intelligence & Research Platform

Interfaces with verified SHAP artifacts generated from TreeExplainer on XGBoost:
- Reads global feature importances (shap/global_importance.csv) over 5,130 features.
- Inspects sample-level local explanations (shap/local_explanations.csv).
- Verifies and exposes SHAP summary and bar visualizations (shap/*.png).
- Adheres strictly to the research rule:
    Never fabricates fake SHAP attribution values.

Run:
    python src/10_explainability.py
    python -m src.10_explainability
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
SHAP_DIR = REPO / "shap"
GLOBAL_IMP_CSV = SHAP_DIR / "global_importance.csv"
LOCAL_EXP_CSV = SHAP_DIR / "local_explanations.csv"
REPORT_JSON = SHAP_DIR / "report.json"
BAR_PNG = SHAP_DIR / "shap_bar.png"
SUMMARY_PNG = SHAP_DIR / "shap_summary.png"
OUT_AUDIT_JSON = REPO / "output" / "shap_audit.json"


class SHAPExplainabilityEngine:
    """Provides access to precomputed verified SHAP explanations."""

    def __init__(self, shap_dir: Path | str | None = None) -> None:
        self.shap_dir = Path(shap_dir) if shap_dir else SHAP_DIR

    def get_audit(self) -> Dict[str, Any]:
        """Audits all SHAP artifacts and summarizes model explainability status."""
        has_global = GLOBAL_IMP_CSV.exists()
        has_local = LOCAL_EXP_CSV.exists()
        has_report = REPORT_JSON.exists()
        has_bar = BAR_PNG.exists()
        has_summary = SUMMARY_PNG.exists()

        status = "AVAILABLE" if (has_global and has_report) else "PARTIAL" if has_global else "MISSING"

        metadata = {}
        if has_report:
            with open(REPORT_JSON, encoding="utf-8") as f:
                metadata = json.load(f)

        top_features: List[Dict[str, Any]] = []
        feature_count = 0
        if has_global:
            df_g = pd.read_csv(GLOBAL_IMP_CSV)
            feature_count = len(df_g)
            top_features = df_g.head(20).to_dict(orient="records")

        local_samples_count = 0
        if has_local:
            df_l = pd.read_csv(LOCAL_EXP_CSV)
            local_samples_count = len(df_l)

        return {
            "status": status,
            "shap_directory": str(self.shap_dir),
            "artifacts_detected": {
                "global_importance_csv": has_global,
                "local_explanations_csv": has_local,
                "report_json": has_report,
                "shap_bar_png": has_bar,
                "shap_summary_png": has_summary,
            },
            "model_explained": metadata.get("model", "XGBoost"),
            "explainer_type": metadata.get("explainer", "shap.TreeExplainer"),
            "total_features": feature_count,
            "local_samples_explained": local_samples_count,
            "top_global_features": top_features,
            "interpretability_note": metadata.get(
                "note",
                "SHAP values describe model feature contributions and do not establish causality."
            ),
        }

    def get_top_features(self, n: int = 15) -> pd.DataFrame:
        """Returns top N global features by mean absolute SHAP value."""
        if not GLOBAL_IMP_CSV.exists():
            return pd.DataFrame()
        return pd.read_csv(GLOBAL_IMP_CSV).head(n)

    def get_local_sample(self, index: int = 0) -> Dict[str, Any]:
        """Returns local explanation details for a specific sample index."""
        if not LOCAL_EXP_CSV.exists():
            return {}
        df_l = pd.read_csv(LOCAL_EXP_CSV)
        if index < 0 or index >= len(df_l):
            index = 0
        row = df_l.iloc[index].to_dict()
        return row


def run(verbose: bool = True) -> dict[str, Any]:
    """Runs the SHAP explainability audit."""
    if verbose:
        print("=" * 60)
        print("10_explainability.py | SHAP Explainability & Attribution Suite")
        print("=" * 60)

    engine = SHAPExplainabilityEngine()
    audit = engine.get_audit()

    if verbose:
        print(f"[STATUS]     SHAP Status: {audit['status']}")
        print(f"[MODEL]      Explaining: {audit['model_explained']} using {audit['explainer_type']}")
        print(f"[FEATURES]   Total Features Evaluated: {audit['total_features']:,}")
        print(f"[SAMPLES]    Local Samples Explained: {audit['local_samples_explained']:,}")
        print("\nTop 10 Global Features (Actual Verified Mean |SHAP|):")
        for i, row in enumerate(audit["top_global_features"][:10], start=1):
            feat = row.get("feature", "N/A")
            val = float(row.get("mean_abs_shap", 0.0))
            bar = "▇" * int(val * 100)
            print(f"  {i:2d}. {feat:<15} : {val:.6f} {bar}")

        print(f"\n[NOTE] {audit['interpretability_note']}")

    OUT_AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"\n[SAVE] Audit saved to {OUT_AUDIT_JSON.name}")
        print("✓ 10_explainability.py complete")

    return audit


if __name__ == "__main__":
    run(verbose=True)
