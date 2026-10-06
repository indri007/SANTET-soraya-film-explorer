from pathlib import Path
import json
import os
import re
import sys
import unicodedata

import pandas as pd
import numpy as np


TARGET = 10_000

BASE_DATA = Path("data/Review Instagram.csv")
RAW_DIR = Path("raw_sources")
OUTPUT_DIR = Path("output")
MODEL_DIR = Path("models")
NETWORK_DIR = Path("network")
SHAP_DIR = Path("shap")


def banner(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def ensure_dirs():
    for d in [OUTPUT_DIR, MODEL_DIR, NETWORK_DIR, SHAP_DIR, RAW_DIR]:
        d.mkdir(parents=True, exist_ok=True)


# ============================================================
# STEP 01
# ============================================================

def step1_data_acquisition():
    banner("STEP 01 — DATA ACQUISITION")

    if not BASE_DATA.exists():
        raise FileNotFoundError(
            f"Dataset utama tidak ditemukan: {BASE_DATA}"
        )

    df = pd.read_csv(BASE_DATA)

    existing = len(df)
    remaining = max(TARGET - existing, 0)

    print(f"Existing records : {existing:,}")
    print(f"Target           : {TARGET:,}")
    print(f"Remaining        : {remaining:,}")

    if existing >= TARGET:
        print("✓ TARGET TERCAPAI")
        status = "TARGET_REACHED"
    else:
        print("\n⚠️ TARGET BELUM TERCAPAI")
        print("Pipeline TIDAK membuat data sintetis.")
        print("Tambahkan dataset/API/export yang valid ke:")
        print(f"  {RAW_DIR}/")
        print("\nStatus: WAITING_FOR_ADDITIONAL_REAL_DATA")
        status = "TARGET_NOT_REACHED"

    return df, status


# ============================================================
# STEP 02
# ============================================================

def normalize_columns(df):
    rename = {}

    for col in df.columns:
        c = str(col).strip().lower()

        if c in ["username", "user_name", "user"]:
            rename[col] = "username"

        elif c in [
            "review text",
            "review_text",
            "text",
            "comment",
            "comments",
            "caption",
            "content"
        ]:
            rename[col] = "original_text"

        elif c in [
            "rating",
            "ratings",
            "label",
            "target"
        ]:
            rename[col] = "rating"

    return df.rename(columns=rename)


def read_data_file(path):
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)

    if suffix == ".json":
        return pd.read_json(path)

    if suffix == ".jsonl":
        return pd.read_json(path, lines=True)

    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path)

    if suffix == ".parquet":
        return pd.read_parquet(path)

    return None


def step2_data_integration(base_df):
    banner("STEP 02 — DATA INTEGRATION")

    frames = []

    base = normalize_columns(base_df.copy())
    base["source"] = "local_dataset"
    base["source_file"] = str(BASE_DATA)
    base["source_type"] = "local_csv"

    frames.append(base)

    for path in sorted(RAW_DIR.iterdir()):
        if not path.is_file():
            continue

        if path.name.startswith("."):
            continue

        try:
            df = read_data_file(path)

            if df is None:
                continue

            df = normalize_columns(df)

            if "original_text" not in df.columns:
                print(f"⚠️ Skip {path}: text column tidak ditemukan")
                continue

            df["source"] = "raw_source"
            df["source_file"] = str(path)
            df["source_type"] = path.suffix.lower().replace(".", "")

            frames.append(df)

            print(
                f"✓ {path.name}: {len(df):,} rows"
            )

        except Exception as e:
            print(
                f"⚠️ Gagal membaca {path}: {e}"
            )

    df = pd.concat(
        frames,
        ignore_index=True,
        sort=False
    )

    if "original_text" not in df.columns:
        raise ValueError(
            "Kolom original_text tidak tersedia."
        )

    df["original_text"] = (
        df["original_text"]
        .fillna("")
        .astype(str)
    )

    df = df[
        df["original_text"].str.strip() != ""
    ].copy()

    df["record_id"] = np.arange(
        1,
        len(df) + 1
    )

    columns = [
        "record_id",
        "username",
        "original_text",
        "rating",
        "source",
        "source_file",
        "source_type"
    ]

    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[columns]

    output = OUTPUT_DIR / "master_raw.csv"
    df.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nIntegrated rows : {len(df):,}")
    print(f"Output          : {output}")

    return df


# ============================================================
# STEP 03
# ============================================================

def count_emoji(text):
    count = 0

    for ch in str(text):
        name = unicodedata.name(ch, "")
        category = unicodedata.category(ch)

        if (
            "EMOJI" in name
            or category in ["So", "Sk"]
        ):
            count += 1

    return count


def clean_text(text):
    text = str(text)

    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"@\w+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # konservatif: batasi karakter berulang ekstrem
    text = re.sub(
        r"(.)\1{4,}",
        r"\1\1\1",
        text
    )

    return text.strip()


def step3_data_cleaning(df):
    banner("STEP 03 — DATA CLEANING")

    out = df.copy()

    out["original_text"] = (
        out["original_text"]
        .fillna("")
        .astype(str)
    )

    out["clean_text"] = (
        out["original_text"]
        .apply(clean_text)
    )

    out["text_length"] = (
        out["original_text"]
        .str.len()
    )

    out["token_count"] = (
        out["clean_text"]
        .str.findall(r"\S+")
        .str.len()
    )

    out["url_count"] = (
        out["original_text"]
        .str.count(
            r"https?://\S+|www\.\S+"
        )
    )

    out["mention_count"] = (
        out["original_text"]
        .str.count(r"@\w+")
    )

    out["hashtag_count"] = (
        out["original_text"]
        .str.count(r"#\w+")
    )

    out["emoji_count"] = (
        out["original_text"]
        .apply(count_emoji)
    )

    output = OUTPUT_DIR / "clean_dataset.csv"

    out.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Rows            : {len(out):,}")
    print(f"Output          : {output}")

    return out


# ============================================================
# STEP 04
# ============================================================

def step4_data_quality(df):
    banner("STEP 04 — DATA QUALITY")

    text = df["original_text"].fillna("").astype(str)

    duplicate_text = int(
        text.duplicated().sum()
    )

    empty_text = int(
        (text.str.strip() == "").sum()
    )

    rating_distribution = {}

    if "rating" in df.columns:
        rating_distribution = (
            df["rating"]
            .value_counts(dropna=False)
            .astype(int)
            .to_dict()
        )

    report = {
        "rows": int(len(df)),
        "duplicate_text": duplicate_text,
        "empty_text": empty_text,
        "unique_users": int(
            df["username"].nunique(
                dropna=True
            )
        ),
        "rating_distribution": {
            str(k): int(v)
            for k, v in rating_distribution.items()
        },
        "target": TARGET,
        "target_reached": bool(
            len(df) >= TARGET
        )
    }

    with open(
        OUTPUT_DIR / "quality_report.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False,
            default=str
        )

    pd.DataFrame(
        [
            {
                "metric": k,
                "value": str(v)
            }
            for k, v in report.items()
        ]
    ).to_csv(
        OUTPUT_DIR / "quality_report.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Rows             : {len(df):,}")
    print(f"Duplicate text   : {duplicate_text}")
    print(f"Empty text       : {empty_text}")
    print(
        "Target reached   : "
        + ("YES" if len(df) >= TARGET else "NO")
    )

    return report


# ============================================================
# STEP 05
# ============================================================

def step5_nlp(df):
    banner("STEP 05 — NLP INTELLIGENCE")

    out = df.copy()

    positive_words = {
        "bagus",
        "baik",
        "suka",
        "mantap",
        "senang",
        "cinta",
        "keren",
        "puas",
        "terima",
        "membantu"
    }

    negative_words = {
        "buruk",
        "kecewa",
        "kesal",
        "marah",
        "lambat",
        "error",
        "bug",
        "gagal",
        "benci",
        "rusak"
    }

    def sentiment(text):
        tokens = set(
            re.findall(
                r"\b\w+\b",
                str(text).lower()
            )
        )

        pos = len(
            tokens & positive_words
        )

        neg = len(
            tokens & negative_words
        )

        if pos > neg:
            return "positive"

        if neg > pos:
            return "negative"

        return "neutral"

    out["baseline_sentiment"] = (
        out["clean_text"]
        .apply(sentiment)
    )

    output = OUTPUT_DIR / "nlp_results.csv"

    out.to_csv(
        output,
        index=False,
        encoding="utf-8-sig"
    )

    print("✓ Baseline sentiment selesai.")
    print(f"Output: {output}")

    return out


# ============================================================
# STEP 06
# ============================================================

def step6_topic_modeling(df):
    banner("STEP 06 — TOPIC MODELING")

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans

    texts = (
        df["clean_text"]
        .fillna("")
        .astype(str)
    )

    vectorizer = TfidfVectorizer(
        max_features=3000,
        ngram_range=(1, 2),
        min_df=2
    )

    X = vectorizer.fit_transform(texts)

    n_clusters = 2

    if len(df) < 10:
        n_clusters = 1

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(X)

    out = df.copy()
    out["topic"] = labels

    out.to_csv(
        OUTPUT_DIR / "topics_dataset.csv",
        index=False,
        encoding="utf-8-sig"
    )

    summary = []

    terms = np.array(
        vectorizer.get_feature_names_out()
    )

    for topic_id in range(n_clusters):
        center = model.cluster_centers_[
            topic_id
        ]

        top_idx = center.argsort()[-10:][::-1]

        representation = ", ".join(
            terms[top_idx]
        )

        count = int(
            (labels == topic_id).sum()
        )

        summary.append(
            {
                "topic": int(topic_id),
                "count": count,
                "representation": representation
            }
        )

    pd.DataFrame(summary).to_csv(
        OUTPUT_DIR / "topics.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Topics: {n_clusters}")

    return out


# ============================================================
# STEP 07
# ============================================================

def step7_network_analysis(df):
    banner("STEP 07 — NETWORK ANALYSIS")

    import networkx as nx

    G = nx.Graph()

    if "username" in df.columns:
        users = (
            df["username"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        users = users[
            users != ""
        ].unique()

        for user in users:
            G.add_node(user)

    nodes = G.number_of_nodes()
    edges = G.number_of_edges()

    density = nx.density(G)

    metrics = {
        "nodes": int(nodes),
        "edges": int(edges),
        "density": float(density),
        "edge_metadata_available": False,
        "note": (
            "Relational network requires valid "
            "edge metadata."
        )
    }

    with open(
        NETWORK_DIR / "metrics.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            metrics,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Nodes   : {nodes:,}")
    print(f"Edges   : {edges:,}")
    print(f"Density : {density:.6f}")
    print(
        "⚠️ Relational network hanya dihitung "
        "jika metadata edge tersedia."
    )

    return metrics


# ============================================================
# STEP 08
# ============================================================

def step8_machine_learning(df):
    banner("STEP 08 — MACHINE LEARNING")

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        classification_report
    )

    target_candidates = [
        "rating",
        "Rating",
        "label",
        "target"
    ]

    target_col = None

    for col in target_candidates:
        if col in df.columns:
            target_col = col
            break

    if target_col is None:
        print("⚠️ Rating/target tidak tersedia.")
        return None, None

    print(f"Target column : {target_col}")

    y = pd.to_numeric(
        df[target_col],
        errors="coerce"
    )

    valid = y.notna()

    X_text = (
        df.loc[valid, "clean_text"]
        .fillna("")
        .astype(str)
    )

    y = y.loc[valid]

    print(f"Valid records : {len(y):,}")
    print(
        "Target values : "
        + str(sorted(y.unique().tolist()))
    )

    print("\nTarget distribution:")
    print(
        y.value_counts()
        .sort_index()
        .to_string()
    )

    if len(y) < 20:
        print("⚠️ Data terlalu sedikit untuk ML.")
        return None, None

    if y.nunique() < 2:
        print(
            "⚠️ Target hanya memiliki satu kelas."
        )
        return None, None

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X_text,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )
    )

    print(f"\nTrain size : {len(X_train):,}")
    print(f"Test size  : {len(X_test):,}")

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=5000,
                    ngram_range=(1, 2),
                    min_df=2
                )
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced"
                )
            )
        ]
    )

    print(
        "\nTraining Logistic Regression..."
    )

    model.fit(
        X_train,
        y_train
    )

    y_pred = model.predict(X_test)

    metrics = {
        "model": (
            "TF-IDF + Logistic Regression"
        ),
        "target": target_col,
        "n_records": int(len(y)),
        "n_train": int(len(y_train)),
        "n_test": int(len(y_test)),
        "accuracy": float(
            accuracy_score(
                y_test,
                y_pred
            )
        ),
        "precision_weighted": float(
            precision_score(
                y_test,
                y_pred,
                average="weighted",
                zero_division=0
            )
        ),
        "recall_weighted": float(
            recall_score(
                y_test,
                y_pred,
                average="weighted",
                zero_division=0
            )
        ),
        "f1_weighted": float(
            f1_score(
                y_test,
                y_pred,
                average="weighted",
                zero_division=0
            )
        ),
        "classification_report": (
            classification_report(
                y_test,
                y_pred,
                zero_division=0,
                output_dict=True
            )
        )
    }

    import joblib

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_DIR /
        "tfidf_logistic_regression.joblib"
    )

    with open(
        MODEL_DIR / "metrics.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            metrics,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n✓ Model selesai.")
    print(
        f"Accuracy : {metrics['accuracy']:.4f}"
    )
    print(
        f"Precision: "
        f"{metrics['precision_weighted']:.4f}"
    )
    print(
        f"Recall   : "
        f"{metrics['recall_weighted']:.4f}"
    )
    print(
        f"F1       : "
        f"{metrics['f1_weighted']:.4f}"
    )

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            y_pred,
            zero_division=0
        )
    )

    print(
        "\nModel:"
        "\nmodels/tfidf_logistic_regression.joblib"
    )

    print(
        "Metrics:"
        "\nmodels/metrics.json"
    )

    return model, metrics


# ============================================================
# STEP 09
# ============================================================

def step9_shap(model):
    banner(
        "STEP 09 — EXPLAINABLE AI / SHAP"
    )

    try:
        import shap

        print(
            f"SHAP version: {shap.__version__}"
        )
        print("✓ SHAP tersedia.")

    except Exception as e:
        print(
            f"⚠️ SHAP tidak tersedia: {e}"
        )

        status = {
            "available": False,
            "model_available": model is not None,
            "full_shap_executed": False
        }

        with open(
            SHAP_DIR / "status.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                status,
                f,
                indent=2
            )

        return status

    if model is None:
        print(
            "Full SHAP akan dijalankan "
            "setelah model final tersedia."
        )

        status = {
            "available": True,
            "model_available": False,
            "full_shap_executed": False
        }

        with open(
            SHAP_DIR / "status.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                status,
                f,
                indent=2
            )

        return status

    print(
        "✓ Model tersedia."
    )

    print(
        "SHAP siap untuk tahap interpretasi "
        "model final."
    )

    status = {
        "available": True,
        "model_available": True,
        "full_shap_executed": False,
        "note": (
            "Full SHAP interpretation should be "
            "performed after final model selection."
        )
    }

    with open(
        SHAP_DIR / "status.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            status,
            f,
            indent=2,
            ensure_ascii=False
        )

    return status


# ============================================================
# STEP 10
# ============================================================

def step10_final_audit(
    df,
    quality_report,
    ml_metrics,
    shap_status,
    network_metrics
):
    banner(
        "STEP 10 — DASHBOARD + FINAL RESEARCH AUDIT"
    )

    final_records = len(df)
    remaining = max(
        TARGET - final_records,
        0
    )

    status = (
        "TARGET_REACHED"
        if final_records >= TARGET
        else "TARGET_NOT_REACHED"
    )

    report = {
        "target": TARGET,
        "final_records": int(final_records),
        "remaining": int(remaining),
        "status": status,
        "quality": quality_report,
        "machine_learning": ml_metrics,
        "shap": shap_status,
        "network": network_metrics,
        "research_ready": (
            final_records >= TARGET
        )
    }

    with open(
        OUTPUT_DIR / "final_report.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False,
            default=str
        )

    print("\n" + "=" * 70)
    print("FINAL STATUS")
    print("=" * 70)

    print(
        f"Target        : {TARGET:,}"
    )

    print(
        f"Final records : {final_records:,}"
    )

    print(
        f"Remaining     : {remaining:,}"
    )

    print(
        f"Status        : {status}"
    )

    if status == "TARGET_REACHED":
        print(
            "\n✓ Dataset memenuhi target."
        )
    else:
        print(
            "\n⚠️ Dataset belum memenuhi target."
        )
        print(
            "Tambahkan data riil sebelum "
            "analisis final penelitian."
        )

    print(
        "\nFinal report: "
        "output/final_report.json"
    )

    return report


# ============================================================
# MAIN
# ============================================================

def main():
    banner(
        "INSTAGRAM 2027 — 10 STEP PYTHON PIPELINE"
    )

    ensure_dirs()

    try:
        # STEP 01
        base_df, acquisition_status = (
            step1_data_acquisition()
        )

        # STEP 02
        master_df = step2_data_integration(
            base_df
        )

        # STEP 03
        clean_df = step3_data_cleaning(
            master_df
        )

        # STEP 04
        quality_report = step4_data_quality(
            clean_df
        )

        # STEP 05
        nlp_df = step5_nlp(
            clean_df
        )

        # STEP 06
        topic_df = step6_topic_modeling(
            nlp_df
        )

        # STEP 07
        network_metrics = (
            step7_network_analysis(
                topic_df
            )
        )

        # STEP 08
        model, ml_metrics = (
            step8_machine_learning(
                topic_df
            )
        )

        # STEP 09
        shap_status = step9_shap(
            model
        )

        # STEP 10
        report = step10_final_audit(
            topic_df,
            quality_report,
            ml_metrics,
            shap_status,
            network_metrics
        )

        print("\n" + "=" * 70)

        if report["status"] == "TARGET_REACHED":
            print(
                "✓ SEMUA 10 TAHAP SELESAI"
            )
        else:
            print(
                "⚠️ 10 TAHAP PROTOTYPE SELESAI"
            )
            print(
                "⚠️ TARGET 10.000 BELUM TERCAPAI"
            )

        print("=" * 70)

    except Exception as e:
        print("\n" + "=" * 70)
        print("PIPELINE ERROR")
        print("=" * 70)
        print(
            type(e).__name__,
            ":",
            str(e)
        )
        print(
            "\nPerbaiki error pada tahap ini "
            "sebelum melanjutkan."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
