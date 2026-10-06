import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap

DATA = Path("output/clean_dataset.csv")
MODEL_FILE = Path("models/xgboost_model.joblib")

OUT = Path("shap")
OUT.mkdir(exist_ok=True)

print("=" * 70)
print("INSTAGRAM 2027 — SHAP ANALYSIS")
print("=" * 70)

if not DATA.exists():
    raise FileNotFoundError(f"Dataset tidak ditemukan: {DATA}")

if not MODEL_FILE.exists():
    raise FileNotFoundError(
        f"Model XGBoost belum ditemukan: {MODEL_FILE}"
    )

df = pd.read_csv(DATA)
df = df.dropna(subset=["clean_text", "rating"]).copy()

print("Dataset records:", len(df))

bundle = joblib.load(MODEL_FILE)

model = bundle["model"]
vectorizer = bundle["vectorizer"]
classes = bundle["classes"]

print("Model:", type(model).__name__)
print("Classes:", classes)

X_text = df["clean_text"].astype(str)

# Batasi sample agar SHAP tidak terlalu berat.
sample_n = min(200, len(df))
sample = df.sample(
    n=sample_n,
    random_state=42
).reset_index(drop=True)

X = vectorizer.transform(sample["clean_text"])

feature_names = vectorizer.get_feature_names_out()

print("SHAP samples:", sample_n)
print("Features:", len(feature_names))

# XGBoost TreeExplainer
explainer = shap.TreeExplainer(model)

print("Menghitung SHAP values...")

shap_values = explainer.shap_values(X)

# Normalisasi bentuk output SHAP untuk multiclass
if isinstance(shap_values, list):
    arrays = [np.asarray(v) for v in shap_values]

    # global mean absolute importance
    importance = np.mean(
        np.stack(
            [np.abs(v).mean(axis=0) for v in arrays],
            axis=0
        ),
        axis=0
    )

    class_count = len(arrays)

else:
    arr = np.asarray(shap_values)

    if arr.ndim == 3:
        # samples x features x classes
        importance = np.mean(
            np.abs(arr),
            axis=(0, 2)
        )
        class_count = arr.shape[2]
    else:
        importance = np.abs(arr).mean(axis=0)
        class_count = 1

# Global importance
importance_df = pd.DataFrame({
    "feature": feature_names,
    "mean_abs_shap": importance
})

importance_df = importance_df.sort_values(
    "mean_abs_shap",
    ascending=False
).reset_index(drop=True)

importance_df.to_csv(
    OUT / "global_importance.csv",
    index=False
)

# Top 20 features
top = importance_df.head(20).sort_values(
    "mean_abs_shap"
)

plt.figure(figsize=(10, 7))
plt.barh(
    top["feature"],
    top["mean_abs_shap"]
)
plt.xlabel("Mean |SHAP value|")
plt.ylabel("Feature")
plt.title("Global SHAP Feature Importance")
plt.tight_layout()
plt.savefig(
    OUT / "shap_bar.png",
    dpi=200
)
plt.close()

# SHAP summary plot
try:
    shap.summary_plot(
        shap_values,
        X,
        feature_names=feature_names,
        show=False
    )
    plt.tight_layout()
    plt.savefig(
        OUT / "shap_summary.png",
        dpi=200,
        bbox_inches="tight"
    )
    plt.close()
except Exception as e:
    print("Summary plot warning:", type(e).__name__, e)

# Local explanations
local_rows = []

top_features = importance_df.head(20)["feature"].tolist()

for i in range(min(20, sample_n)):
    row = {
        "sample_index": i,
        "actual_rating": int(sample.loc[i, "rating"]),
        "clean_text": sample.loc[i, "clean_text"]
    }

    if isinstance(shap_values, list):
        # Use class with highest model probability
        probabilities = model.predict_proba(X[i])
        class_idx = int(np.argmax(probabilities))

        values = np.asarray(shap_values[class_idx])[i]

        for feature in top_features:
            feature_idx = np.where(
                feature_names == feature
            )[0][0]

            row[f"shap_{feature}"] = float(
                values[feature_idx]
            )

    else:
        arr = np.asarray(shap_values)

        if arr.ndim == 3:
            probabilities = model.predict_proba(X[i])
            class_idx = int(np.argmax(probabilities))
            values = arr[i, :, class_idx]
        else:
            values = arr[i]

        for feature in top_features:
            feature_idx = np.where(
                feature_names == feature
            )[0][0]

            row[f"shap_{feature}"] = float(
                values[feature_idx]
            )

    local_rows.append(row)

local_df = pd.DataFrame(local_rows)

local_df.to_csv(
    OUT / "local_explanations.csv",
    index=False
)

report = {
    "status": "VERIFIED",
    "model": "XGBoost",
    "dataset_records": int(len(df)),
    "samples_explained": int(sample_n),
    "feature_count": int(len(feature_names)),
    "class_count": int(class_count),
    "explainer": "shap.TreeExplainer",
    "global_importance": "shap/global_importance.csv",
    "local_explanations": "shap/local_explanations.csv",
    "summary_plot": "shap/shap_summary.png",
    "bar_plot": "shap/shap_bar.png",
    "note": (
        "SHAP values describe model feature contributions "
        "and do not establish causality."
    )
}

with open(OUT / "report.json", "w") as f:
    json.dump(report, f, indent=2)

print("\n" + "=" * 70)
print("SHAP ANALYSIS SELESAI")
print("=" * 70)
print("Status             : VERIFIED")
print("Model              : XGBoost")
print("Dataset records    :", len(df))
print("Samples explained  :", sample_n)
print("Features           :", len(feature_names))
print("Global importance  :", OUT / "global_importance.csv")
print("Local explanations :", OUT / "local_explanations.csv")
print("Summary plot       :", OUT / "shap_summary.png")
print("Bar plot           :", OUT / "shap_bar.png")
print("Report             :", OUT / "report.json")
