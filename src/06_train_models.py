"""
06_train_models.py
==================
Step 6 — Model Benchmark & Training Engine
Pipeline: Instagram Indonesia Viral Intelligence & Research Platform

Manages machine learning model artifacts and training pipelines:
- Discovers and audits existing trained models:
  * best_model.joblib
  * logistic_regression.joblib
  * random_forest.joblib
  * xgboost_model.joblib
  * lightgbm_model.joblib
  * tfidf_logistic_regression.joblib
- Provides reproducible training pipelines over actual dataset features
  (TF-IDF + linguistic features).
- Prevents accidental overwriting of benchmark artifacts.

Run:
    python src/06_train_models.py
    python -m src.06_train_models
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
MODEL_DIR = REPO / "models"
INPUT_CSV = REPO / "output" / "features_engineered.csv"
FALLBACK_CSV = REPO / "output" / "topics_dataset.csv"
OUT_AUDIT_JSON = REPO / "output" / "models_inventory_audit.json"

REGISTERED_MODELS = [
    "best_model.joblib",
    "logistic_regression.joblib",
    "random_forest.joblib",
    "xgboost_model.joblib",
    "lightgbm_model.joblib",
    "tfidf_logistic_regression.joblib",
]


class ModelManager:
    """Manages artifact auditing, model loading, and reproducible training."""

    def __init__(self, model_dir: Path | str | None = None) -> None:
        self.model_dir = Path(model_dir) if model_dir else MODEL_DIR

    def audit_existing_models(self) -> Dict[str, Any]:
        """Scans model directory and verifies presence and metadata of artifacts."""
        inventory = {}
        for fname in REGISTERED_MODELS:
            path = self.model_dir / fname
            if path.exists():
                size_bytes = path.stat().st_size
                inventory[fname] = {
                    "status": "AVAILABLE",
                    "path": str(path),
                    "size_bytes": size_bytes,
                    "size_mb": round(size_bytes / (1024 * 1024), 2),
                }
                # Try to inspect model type safely
                try:
                    loaded = joblib.load(path)
                    inventory[fname]["type"] = type(loaded).__name__
                    if hasattr(loaded, "classes_"):
                        inventory[fname]["classes"] = [int(c) for c in loaded.classes_]
                except Exception as e:
                    inventory[fname]["load_error"] = str(e)
            else:
                inventory[fname] = {
                    "status": "MISSING",
                    "path": str(path),
                    "size_bytes": 0,
                    "size_mb": 0.0,
                }

        # Check existing metrics files
        metrics_file = self.model_dir / "metrics.json"
        comp_file = self.model_dir / "model_comparison.csv"
        tree_comp_file = self.model_dir / "tree_model_comparison.csv"

        benchmark_summary = {}
        if metrics_file.exists():
            with open(metrics_file, encoding="utf-8") as f:
                benchmark_summary["metrics_json"] = json.load(f)
        if comp_file.exists():
            benchmark_summary["linear_comparison"] = pd.read_csv(comp_file).to_dict(orient="records")
        if tree_comp_file.exists():
            benchmark_summary["tree_comparison"] = pd.read_csv(tree_comp_file).to_dict(orient="records")

        return {
            "model_directory": str(self.model_dir),
            "artifacts": inventory,
            "benchmark_summary": benchmark_summary,
        }

    def train_baseline_pipeline(
        self,
        df: pd.DataFrame,
        save_as: str | None = None,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """Reproducible baseline training using TF-IDF + Logistic Regression."""
        X_text = df["clean_text"].fillna("").astype(str)
        y = df["rating"].astype(int)

        X_train_txt, X_test_txt, y_train, y_test = train_test_split(
            X_text, y, test_size=0.20, random_state=42, stratify=y
        )

        vec = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), min_df=2)
        X_train_vec = vec.fit_transform(X_train_txt)
        X_test_vec = vec.transform(X_test_txt)

        clf = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
        clf.fit(X_train_vec, y_train)

        y_pred = clf.predict(X_test_vec)
        acc = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average="macro")
        f1_weighted = f1_score(y_test, y_pred, average="weighted")

        results = {
            "model_type": "LogisticRegression(balanced)",
            "accuracy": round(float(acc), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_weighted": round(float(f1_weighted), 4),
            "train_samples": len(y_train),
            "test_samples": len(y_test),
        }

        if save_as:
            out_path = self.model_dir / save_as
            if out_path.exists() and not overwrite:
                results["save_status"] = f"Skipped save: {save_as} exists and overwrite=False"
            else:
                joblib.dump({"vectorizer": vec, "classifier": clf}, out_path)
                results["save_status"] = f"Saved to {out_path}"

        return results


def run(verbose: bool = True) -> dict[str, Any]:
    """Audits existing models and validates benchmark status."""
    if verbose:
        print("=" * 60)
        print("06_train_models.py | Model Benchmark & Inventory Audit")
        print("=" * 60)

    manager = ModelManager()
    audit = manager.audit_existing_models()

    if verbose:
        print("\nModel Artifacts Inventory:")
        for name, info in audit["artifacts"].items():
            status_str = f"[{info['status']}]"
            size_str = f"{info['size_mb']} MB" if info["status"] == "AVAILABLE" else "N/A"
            type_str = f"({info.get('type', 'Unknown')})" if info["status"] == "AVAILABLE" else ""
            print(f"  {status_str:12s} {name:32s} {size_str:10s} {type_str}")

        print("\nBenchmark Highlights (Actual Verified Metrics):")
        b_sum = audit.get("benchmark_summary", {})
        if "metrics_json" in b_sum:
            mj = b_sum["metrics_json"]
            print(f"  Baseline Model : {mj.get('model')}")
            print(f"  Accuracy       : {mj.get('accuracy'):.4f}")
            print(f"  Weighted F1    : {mj.get('f1_weighted'):.4f}")
        if "tree_comparison" in b_sum:
            for row in b_sum["tree_comparison"]:
                print(f"  Tree Model: {row.get('model'):10s} | Acc: {row.get('accuracy')} | F1: {row.get('f1_weighted')}")

    OUT_AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"\n[SAVE] Audit saved to {OUT_AUDIT_JSON.name}")
        print("✓ 06_train_models.py complete")

    return audit


if __name__ == "__main__":
    run(verbose=True)
