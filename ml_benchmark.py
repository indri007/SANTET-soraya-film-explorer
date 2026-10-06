import os
import json
from datetime import datetime

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

os.makedirs("models", exist_ok=True)
os.makedirs("output", exist_ok=True)

print("=" * 70)
print("INSTAGRAM 2027 — ML BENCHMARK")
print("=" * 70)

df = pd.read_csv("output/clean_dataset.csv")

text_col = next(
    (c for c in ["clean_text", "original_text", "Review Text"] if c in df.columns),
    None
)

target_col = next(
    (c for c in ["rating", "Rating"] if c in df.columns),
    None
)

if text_col is None:
    raise ValueError("Kolom teks tidak ditemukan.")

if target_col is None:
    raise ValueError("Kolom rating tidak ditemukan.")

df = df.dropna(subset=[text_col, target_col]).copy()

df[text_col] = df[text_col].astype(str)
df[target_col] = pd.to_numeric(df[target_col], errors="coerce")
df = df.dropna(subset=[target_col])

X = df[text_col]
y = df[target_col].astype(int)

print(f"Text column   : {text_col}")
print(f"Target column : {target_col}")
print(f"Records       : {len(df)}")
print(f"Classes       : {sorted(y.unique())}")

print("\nClass distribution:")
print(y.value_counts().sort_index())

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"\nTrain size : {len(X_train)}")
print(f"Test size  : {len(X_test)}")

models = {
    "logistic_regression": Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_features=20000,
            sublinear_tf=True
        )),
        ("classifier", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42
        ))
    ]),

    "random_forest": Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_features=10000,
            sublinear_tf=True
        )),
        ("classifier", RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])
}

results = []
trained_models = {}

for name, model in models.items():

    print("\n" + "-" * 70)
    print(f"TRAINING: {name}")
    print("-" * 70)

    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    metrics = {
        "model": name,
        "accuracy": accuracy_score(y_test, pred),
        "precision_macro": precision_score(y_test, pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_test, pred, average="macro", zero_division=0),
        "f1_macro": f1_score(y_test, pred, average="macro", zero_division=0),
        "precision_weighted": precision_score(y_test, pred, average="weighted", zero_division=0),
        "recall_weighted": recall_score(y_test, pred, average="weighted", zero_division=0),
        "f1_weighted": f1_score(y_test, pred, average="weighted", zero_division=0)
    }

    results.append(metrics)
    trained_models[name] = model

    print(f"Accuracy          : {metrics['accuracy']:.4f}")
    print(f"Precision Macro    : {metrics['precision_macro']:.4f}")
    print(f"Recall Macro       : {metrics['recall_macro']:.4f}")
    print(f"F1 Macro           : {metrics['f1_macro']:.4f}")
    print(f"Precision Weighted : {metrics['precision_weighted']:.4f}")
    print(f"Recall Weighted    : {metrics['recall_weighted']:.4f}")
    print(f"F1 Weighted        : {metrics['f1_weighted']:.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, pred, zero_division=0))

    joblib.dump(model, f"models/{name}.joblib")

    labels = sorted(y.unique())
    cm = confusion_matrix(y_test, pred, labels=labels)

    pd.DataFrame(
        cm,
        index=[f"actual_{x}" for x in labels],
        columns=[f"predicted_{x}" for x in labels]
    ).to_csv(f"output/confusion_matrix_{name}.csv")

comparison = pd.DataFrame(results)
comparison = comparison.sort_values("f1_macro", ascending=False)
comparison.to_csv("models/model_comparison.csv", index=False)

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)
print(comparison.to_string(index=False))

best_model_name = comparison.iloc[0]["model"]
best_model = trained_models[best_model_name]

joblib.dump(best_model, "models/best_model.joblib")

print(f"\nBest model berdasarkan F1 Macro: {best_model_name}")

print("\n" + "=" * 70)
print("5-FOLD CROSS VALIDATION")
print("=" * 70)

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

cv_rows = []

for name, model in models.items():

    print(f"\nCV: {name}")

    scores = cross_validate(
        model,
        X,
        y,
        cv=cv,
        scoring=[
            "accuracy",
            "precision_macro",
            "recall_macro",
            "f1_macro"
        ],
        n_jobs=1
    )

    row = {
        "model": name,
        "accuracy_mean": scores["test_accuracy"].mean(),
        "accuracy_std": scores["test_accuracy"].std(),
        "precision_macro_mean": scores["test_precision_macro"].mean(),
        "precision_macro_std": scores["test_precision_macro"].std(),
        "recall_macro_mean": scores["test_recall_macro"].mean(),
        "recall_macro_std": scores["test_recall_macro"].std(),
        "f1_macro_mean": scores["test_f1_macro"].mean(),
        "f1_macro_std": scores["test_f1_macro"].std()
    }

    cv_rows.append(row)

    print(
        f"Accuracy : {row['accuracy_mean']:.4f} "
        f"+/- {row['accuracy_std']:.4f}"
    )

    print(
        f"F1 Macro : {row['f1_macro_mean']:.4f} "
        f"+/- {row['f1_macro_std']:.4f}"
    )

pd.DataFrame(cv_rows).to_csv(
    "models/cross_validation.csv",
    index=False
)

best_pred = best_model.predict(X_test)

error_df = pd.DataFrame({
    "clean_text": X_test.values,
    "actual_rating": y_test.values,
    "predicted_rating": best_pred
})

error_df["correct"] = (
    error_df["actual_rating"] ==
    error_df["predicted_rating"]
)

if hasattr(best_model, "predict_proba"):
    error_df["model_confidence"] = (
        best_model.predict_proba(X_test).max(axis=1)
    )
else:
    error_df["model_confidence"] = np.nan

error_df[
    error_df["correct"] == False
].sort_values(
    "model_confidence",
    ascending=False
).to_csv(
    "output/ml_error_analysis.csv",
    index=False
)

class_distribution = (
    y.value_counts()
    .sort_index()
    .rename_axis("rating")
    .reset_index(name="count")
)

class_distribution["percentage"] = (
    class_distribution["count"] / len(y) * 100
)

class_distribution.to_csv(
    "output/class_distribution.csv",
    index=False
)

metadata = {
    "best_model": best_model_name,
    "training_records": len(X_train),
    "test_records": len(X_test),
    "total_valid_records": len(df),
    "target_classes": sorted([int(x) for x in y.unique()]),
    "random_state": 42,
    "features": "TF-IDF unigram + bigram",
    "models": list(models.keys()),
    "metrics": results,
    "dataset_target": 10000,
    "current_records": 1000,
    "remaining_records": 9000,
    "status": "TARGET_NOT_REACHED",
    "timestamp": datetime.now().isoformat()
}

with open("models/model_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("\n" + "=" * 70)
print("ML BENCHMARK SELESAI")
print("=" * 70)

print("Current   : 1,000")
print("Target    : 10,000")
print("Remaining : 9,000")
print("Status    : TARGET_NOT_REACHED")

print("\nOutput:")
print("models/model_comparison.csv")
print("models/cross_validation.csv")
print("models/best_model.joblib")
print("models/model_metadata.json")
print("output/ml_error_analysis.csv")
print("output/class_distribution.csv")
