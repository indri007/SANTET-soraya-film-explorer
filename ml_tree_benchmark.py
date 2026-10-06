import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier


DATA = Path("output/clean_dataset.csv")
OUT = Path("models")
OUT.mkdir(exist_ok=True)

RANDOM_STATE = 42

df = pd.read_csv(DATA)
df = df.dropna(subset=["clean_text", "rating"]).copy()

X_text = df["clean_text"].astype(str)
y = df["rating"].astype(int)

print("=" * 70)
print("INSTAGRAM 2027 — XGBOOST + LIGHTGBM BENCHMARK")
print("=" * 70)
print("Records:", len(df))
print("Classes:", sorted(y.unique().tolist()))

X_train_text, X_test_text, y_train, y_test = train_test_split(
    X_text,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)

vectorizer = TfidfVectorizer(
    min_df=2,
    max_features=10000,
    ngram_range=(1, 2),
    sublinear_tf=True,
)

X_train = vectorizer.fit_transform(X_train_text)
X_test = vectorizer.transform(X_test_text)

print("Train size:", X_train.shape[0])
print("Test size :", X_test.shape[0])
print("Features  :", X_train.shape[1])

# XGBoost labels must be zero-based
classes = sorted(y.unique())
class_to_idx = {c: i for i, c in enumerate(classes)}
y_train_xgb = y_train.map(class_to_idx)
y_test_xgb = y_test.map(class_to_idx)

models = {
    "xgboost": XGBClassifier(
        n_estimators=250,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="multi:softprob",
        num_class=len(classes),
        eval_metric="mlogloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),
    "lightgbm": LGBMClassifier(
        n_estimators=250,
        max_depth=-1,
        num_leaves=31,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="multiclass",
        num_class=len(classes),
        random_state=RANDOM_STATE,
        n_jobs=-1,
        verbosity=-1,
    ),
}

results = []
cv_results = []

for name, model in models.items():
    print("\n" + "-" * 70)
    print("TRAINING:", name)
    print("-" * 70)

    try:
        model.fit(X_train, y_train_xgb)

        pred_idx = model.predict(X_test)
        pred_idx = np.asarray(pred_idx).astype(int)
        pred = np.array([classes[i] for i in pred_idx])

        metrics = {
            "model": name,
            "status": "VERIFIED",
            "accuracy": accuracy_score(y_test, pred),
            "precision_macro": precision_score(
                y_test, pred, average="macro", zero_division=0
            ),
            "recall_macro": recall_score(
                y_test, pred, average="macro", zero_division=0
            ),
            "f1_macro": f1_score(
                y_test, pred, average="macro", zero_division=0
            ),
            "precision_weighted": precision_score(
                y_test, pred, average="weighted", zero_division=0
            ),
            "recall_weighted": recall_score(
                y_test, pred, average="weighted", zero_division=0
            ),
            "f1_weighted": f1_score(
                y_test, pred, average="weighted", zero_division=0
            ),
            "error": "",
        }

        results.append(metrics)

        print(f"Accuracy          : {metrics['accuracy']:.4f}")
        print(f"Precision Macro    : {metrics['precision_macro']:.4f}")
        print(f"Recall Macro       : {metrics['recall_macro']:.4f}")
        print(f"F1 Macro           : {metrics['f1_macro']:.4f}")
        print(f"Precision Weighted : {metrics['precision_weighted']:.4f}")
        print(f"Recall Weighted    : {metrics['recall_weighted']:.4f}")
        print(f"F1 Weighted        : {metrics['f1_weighted']:.4f}")

        # 5-fold CV on the training partition only
        scoring = {
            "accuracy": "accuracy",
            "precision_macro": "precision_macro",
            "recall_macro": "recall_macro",
            "f1_macro": "f1_macro",
        }

        cv = StratifiedKFold(
            n_splits=5,
            shuffle=True,
            random_state=RANDOM_STATE,
        )

        cv_score = cross_validate(
            model,
            X_train,
            y_train_xgb,
            cv=cv,
            scoring=scoring,
            n_jobs=1,
            error_score="raise",
        )

        cv_row = {
            "model": name,
            "status": "VERIFIED",
            "accuracy_mean": cv_score["test_accuracy"].mean(),
            "accuracy_std": cv_score["test_accuracy"].std(),
            "precision_macro_mean": cv_score["test_precision_macro"].mean(),
            "precision_macro_std": cv_score["test_precision_macro"].std(),
            "recall_macro_mean": cv_score["test_recall_macro"].mean(),
            "recall_macro_std": cv_score["test_recall_macro"].std(),
            "f1_macro_mean": cv_score["test_f1_macro"].mean(),
            "f1_macro_std": cv_score["test_f1_macro"].std(),
            "error": "",
        }

        cv_results.append(cv_row)

        print(
            f"CV Accuracy : {cv_row['accuracy_mean']:.4f} "
            f"+/- {cv_row['accuracy_std']:.4f}"
        )
        print(
            f"CV F1 Macro : {cv_row['f1_macro_mean']:.4f} "
            f"+/- {cv_row['f1_macro_std']:.4f}"
        )

        import joblib

        joblib.dump(
            {
                "model": model,
                "vectorizer": vectorizer,
                "classes": classes,
            },
            OUT / f"{name}_model.joblib",
        )

    except Exception as e:
        error = f"{type(e).__name__}: {e}"

        print("FAILED:", error)

        results.append(
            {
                "model": name,
                "status": "FAILED",
                "accuracy": np.nan,
                "precision_macro": np.nan,
                "recall_macro": np.nan,
                "f1_macro": np.nan,
                "precision_weighted": np.nan,
                "recall_weighted": np.nan,
                "f1_weighted": np.nan,
                "error": error,
            }
        )

        cv_results.append(
            {
                "model": name,
                "status": "FAILED",
                "accuracy_mean": np.nan,
                "accuracy_std": np.nan,
                "precision_macro_mean": np.nan,
                "precision_macro_std": np.nan,
                "recall_macro_mean": np.nan,
                "recall_macro_std": np.nan,
                "f1_macro_mean": np.nan,
                "f1_macro_std": np.nan,
                "error": error,
            }
        )

pd.DataFrame(results).to_csv(
    OUT / "tree_model_comparison.csv",
    index=False,
)

pd.DataFrame(cv_results).to_csv(
    OUT / "tree_cross_validation.csv",
    index=False,
)

audit = {
    "dataset_records": int(len(df)),
    "target_records": 10000,
    "remaining_records": int(max(0, 10000 - len(df))),
    "dataset_status": (
        "TARGET_REACHED" if len(df) >= 10000 else "TARGET_NOT_REACHED"
    ),
    "executed_at": datetime.now().isoformat(),
    "models": results,
    "cross_validation": cv_results,
}

with open(OUT / "tree_benchmark_audit.json", "w") as f:
    json.dump(audit, f, indent=2, default=str)

print("\n" + "=" * 70)
print("TREE BENCHMARK SELESAI")
print("=" * 70)
print("Dataset :", len(df))
print("Target  : 10000")
print("Status  :", audit["dataset_status"])
print("Output  : models/tree_model_comparison.csv")
print("Output  : models/tree_cross_validation.csv")
print("Output  : models/tree_benchmark_audit.json")
