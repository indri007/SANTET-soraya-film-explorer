"""
07_evaluate.py
==============
Step 7 — Model Evaluation & Performance Analytics
Pipeline: Instagram Indonesia Viral Intelligence & Research Platform

Consolidates model benchmarking, cross-validation metrics, confusion matrices,
and error distribution across classifiers:
- Reads actual verified evaluation metrics from models/ and output/.
- Provides evaluators for Accuracy, Weighted F1, Macro F1, Precision, Recall.
- Performs error analysis breaking down misclassification patterns
  across 5-star ratings (Rating 1 through 5).

Run:
    python src/07_evaluate.py
    python -m src.07_evaluate
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
MODEL_DIR = REPO / "models"
OUTPUT_DIR = REPO / "output"
OUT_AUDIT_JSON = OUTPUT_DIR / "evaluation_audit.json"


class ModelEvaluator:
    """Evaluates classifier outputs and aggregates verified research benchmarks."""

    def __init__(self) -> None:
        self.metrics_json_path = MODEL_DIR / "metrics.json"
        self.model_comp_path = MODEL_DIR / "model_comparison.csv"
        self.tree_comp_path = MODEL_DIR / "tree_model_comparison.csv"
        self.error_analysis_path = OUTPUT_DIR / "ml_error_analysis.csv"

    def load_benchmark_summary(self) -> Dict[str, Any]:
        """Loads and cross-references all existing model benchmarks."""
        summary: Dict[str, Any] = {
            "status": "AVAILABLE",
            "models_benchmarked": [],
            "detailed_reports": {},
        }

        # 1. Base Logistic Regression metrics
        if self.metrics_json_path.exists():
            with open(self.metrics_json_path, encoding="utf-8") as f:
                data = json.load(f)
                summary["detailed_reports"]["baseline_logistic_regression"] = data
                summary["models_benchmarked"].append({
                    "model": data.get("model", "TF-IDF + Logistic Regression"),
                    "accuracy": data.get("accuracy"),
                    "f1_weighted": data.get("f1_weighted"),
                    "precision_weighted": data.get("precision_weighted"),
                    "recall_weighted": data.get("recall_weighted"),
                })

        # 2. Linear / Ensemble comparison table
        if self.model_comp_path.exists():
            df_comp = pd.read_csv(self.model_comp_path)
            summary["linear_comparison"] = df_comp.to_dict(orient="records")
            for _, r in df_comp.iterrows():
                summary["models_benchmarked"].append({
                    "model": str(r.get("model")),
                    "accuracy": float(r.get("accuracy", 0.0)),
                    "f1_weighted": float(r.get("f1_weighted", 0.0)),
                    "precision_weighted": float(r.get("precision_weighted", 0.0)),
                    "recall_weighted": float(r.get("recall_weighted", 0.0)),
                })

        # 3. Tree comparison table (XGBoost, LightGBM)
        if self.tree_comp_path.exists():
            df_tree = pd.read_csv(self.tree_comp_path)
            summary["tree_comparison"] = df_tree.to_dict(orient="records")
            for _, r in df_tree.iterrows():
                summary["models_benchmarked"].append({
                    "model": f"tree_{r.get('model')}",
                    "accuracy": float(r.get("accuracy", 0.0)),
                    "f1_weighted": float(r.get("f1_weighted", 0.0)),
                    "precision_weighted": float(r.get("precision_weighted", 0.0)),
                    "recall_weighted": float(r.get("recall_weighted", 0.0)),
                })

        # 4. Error analysis inspection
        if self.error_analysis_path.exists():
            df_err = pd.read_csv(self.error_analysis_path)
            summary["error_analysis"] = {
                "total_evaluated_samples": len(df_err),
                "error_rate": round(float((df_err["rating"] != df_err["predicted"]).mean()), 4) if "predicted" in df_err.columns and "rating" in df_err.columns else None,
                "confusion_pairs": (
                    df_err.groupby(["rating", "predicted"]).size().reset_index(name="count").to_dict(orient="records")
                    if "predicted" in df_err.columns and "rating" in df_err.columns else []
                ),
            }

        return summary

    def evaluate_predictions(
        self,
        y_true: list[int] | np.ndarray | pd.Series,
        y_pred: list[int] | np.ndarray | pd.Series,
        labels: list[int] | None = None
    ) -> Dict[str, Any]:
        """Calculates multiclass evaluation metrics for given predictions."""
        acc = accuracy_score(y_true, y_pred)
        f1_w = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        f1_m = f1_score(y_true, y_pred, average="macro", zero_division=0)
        prec_w = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        rec_w = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()
        clf_rep = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)

        return {
            "accuracy": round(float(acc), 4),
            "f1_weighted": round(float(f1_w), 4),
            "f1_macro": round(float(f1_m), 4),
            "precision_weighted": round(float(prec_w), 4),
            "recall_weighted": round(float(rec_w), 4),
            "confusion_matrix": cm,
            "classification_report": clf_rep,
        }


def run(verbose: bool = True) -> dict[str, Any]:
    """Runs evaluation benchmark audit."""
    if verbose:
        print("=" * 60)
        print("07_evaluate.py | Multi-Model Performance & Error Evaluation")
        print("=" * 60)

    evaluator = ModelEvaluator()
    summary = evaluator.load_benchmark_summary()

    if verbose:
        print(f"\n[BENCHMARK] Loaded {len(summary['models_benchmarked'])} model benchmark results:")
        print(f"  {'Model':<30} | {'Accuracy':<10} | {'F1-Weighted':<12}")
        print("  " + "-" * 56)
        for m in summary["models_benchmarked"]:
            acc = f"{m.get('accuracy', 0):.4f}" if m.get("accuracy") is not None else "N/A"
            f1 = f"{m.get('f1_weighted', 0):.4f}" if m.get("f1_weighted") is not None else "N/A"
            print(f"  {m['model']:<30} | {acc:<10} | {f1:<12}")

        if "error_analysis" in summary:
            err = summary["error_analysis"]
            print(f"\n[ERROR ANALYSIS] Total errors analyzed: {err['total_evaluated_samples']} samples")
            if err.get("error_rate") is not None:
                print(f"  Error Rate: {err['error_rate'] * 100:.2f}% (Accuracy: {(1 - err['error_rate']) * 100:.2f}%)")

    OUT_AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"\n[SAVE] Audit saved to {OUT_AUDIT_JSON.name}")
        print("✓ 07_evaluate.py complete")

    return summary


if __name__ == "__main__":
    run(verbose=True)
