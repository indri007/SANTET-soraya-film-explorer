"""
03_indobert.py
==============
Step 3 — IndoBERT Neural Feature Extractor & Inference Suite
Pipeline: Instagram Indonesia Viral Intelligence & Research Platform

Executes actual batch inference on Indonesian Instagram review data using
locally cached pretrained transformer models:
- indobenchmark/indobert-base-p1: Contextual 768-d sentence embeddings.
- mdhugol/indonesia-bert-sentiment-classification: Deep sentiment probabilities.
- Affective Emotion Classification: Indonesian emotion dimensions (joy, sadness,
  anger, fear, surprise, neutral).

Outputs:
  output/indobert_features.csv
  output/indobert_embeddings.npy
  output/indobert_embedding_index.csv
  output/indobert_report.json

Run:
    python src/03_indobert.py
    python -m src.03_indobert
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import torch

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
INPUT_CSV = REPO / "output" / "master_instagram_10000.csv"
FALLBACK_CSV = REPO / "data" / "Review Instagram.csv"

OUT_FEATURES_CSV = REPO / "output" / "indobert_features.csv"
OUT_EMBEDDINGS_NPY = REPO / "output" / "indobert_embeddings.npy"
OUT_INDEX_CSV = REPO / "output" / "indobert_embedding_index.csv"
OUT_REPORT_JSON = REPO / "output" / "indobert_report.json"

# Affective Lexicons
JOY_WORDS = {'suka', 'senang', 'cinta', 'keren', 'mantap', 'bagus', 'puas', 'terima', 'asik', 'top', 'hebat', 'nyaman'}
SAD_WORDS = {'sedih', 'kecewa', 'hilang', 'rusak', 'sayang', 'kenangan', 'menyesal', 'tangis', 'rugi'}
ANGER_WORDS = {'kesal', 'marah', 'buruk', 'parah', 'benci', 'sampah', 'jelek', 'goblok', 'anjing', 'babi', 'bobrok', 'blokir'}
FEAR_WORDS = {'takut', 'bahaya', 'hack', 'curiga', 'banned', 'ancam'}
SURPRISE_WORDS = {'kaget', 'tiba', 'heran', 'kok', 'kenapa', 'masa', 'aneh', 'ajaib'}


class IndoBERTInferenceEngine:
    """Production interface and batch inference engine for IndoBERT."""

    def __init__(self) -> None:
        self.device = 'mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu'

    def classify_emotion(self, text: str, sentiment: str) -> str:
        tokens = set(str(text).lower().split())
        if tokens & ANGER_WORDS:
            return 'anger'
        if tokens & SAD_WORDS:
            return 'sadness'
        if tokens & FEAR_WORDS:
            return 'fear'
        if tokens & SURPRISE_WORDS:
            return 'surprise'
        if tokens & JOY_WORDS:
            return 'joy'
        if sentiment == 'negative':
            return 'anger'
        if sentiment == 'positive':
            return 'joy'
        return 'neutral'

    def run_inference(self, df: pd.DataFrame, batch_size: int = 32) -> Dict[str, Any]:
        from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification

        t0 = time.time()
        text_col = 'original_text' if 'original_text' in df.columns else 'Review Text'
        texts = df[text_col].fillna('').astype(str).tolist()

        # Load models
        tok_emb = AutoTokenizer.from_pretrained('indobenchmark/indobert-base-p1', local_files_only=True)
        mod_emb = AutoModel.from_pretrained('indobenchmark/indobert-base-p1', local_files_only=True).to(self.device)
        mod_emb.eval()

        tok_sent = AutoTokenizer.from_pretrained('mdhugol/indonesia-bert-sentiment-classification', local_files_only=True)
        mod_sent = AutoModelForSequenceClassification.from_pretrained('mdhugol/indonesia-bert-sentiment-classification', local_files_only=True).to(self.device)
        mod_sent.eval()

        label_map = {0: 'positive', 1: 'neutral', 2: 'negative'}
        embeddings_list = []
        sent_preds = []
        sent_confs = []
        pos_probs = []
        neu_probs = []
        neg_probs = []

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]

            # 768-d Contextual Representation
            inp_emb = tok_emb(batch_texts, padding=True, truncation=True, max_length=128, return_tensors='pt').to(self.device)
            with torch.no_grad():
                out_emb = mod_emb(**inp_emb)
                cls_vecs = out_emb.last_hidden_state[:, 0, :].cpu().numpy()
                embeddings_list.append(cls_vecs)

            # Sentiment Classification
            inp_sent = tok_sent(batch_texts, padding=True, truncation=True, max_length=128, return_tensors='pt').to(self.device)
            with torch.no_grad():
                logits = mod_sent(**inp_sent).logits
                probs = torch.softmax(logits, dim=-1).cpu().numpy()
                for p in probs:
                    pred_idx = int(np.argmax(p))
                    sent_preds.append(label_map[pred_idx])
                    sent_confs.append(float(p[pred_idx]))
                    pos_probs.append(float(p[0]))
                    neu_probs.append(float(p[1]))
                    neg_probs.append(float(p[2]))

        all_embeddings = np.vstack(embeddings_list)
        emotions = [self.classify_emotion(t, s) for t, s in zip(texts, sent_preds)]

        # Save files
        OUT_EMBEDDINGS_NPY.parent.mkdir(parents=True, exist_ok=True)
        np.save(OUT_EMBEDDINGS_NPY, all_embeddings)

        record_ids = df['record_id'].tolist() if 'record_id' in df.columns else [f'IG-{i+1:06d}' for i in range(len(df))]
        pd.DataFrame({
            'embedding_index': range(len(df)),
            'record_id': record_ids,
            'embedding_dim': all_embeddings.shape[1]
        }).to_csv(OUT_INDEX_CSV, index=False)

        features_df = pd.DataFrame({
            'record_id': record_ids,
            'text': texts,
            'indobert_sentiment': sent_preds,
            'sentiment_confidence': [round(c, 4) for c in sent_confs],
            'prob_positive': [round(p, 4) for p in pos_probs],
            'prob_neutral': [round(p, 4) for p in neu_probs],
            'prob_negative': [round(p, 4) for p in neg_probs],
            'emotion': emotions,
            'embedding_index': range(len(df))
        })
        features_df.to_csv(OUT_FEATURES_CSV, index=False, encoding='utf-8-sig')

        elapsed = round(time.time() - t0, 2)
        report = {
            'model_name': 'indobenchmark/indobert-base-p1 & mdhugol/indonesia-bert-sentiment-classification',
            'model_source': 'Local HuggingFace Cache (~/.cache/huggingface/hub)',
            'device': self.device,
            'number_of_records': len(df),
            'batch_size': batch_size,
            'inference_status': 'AVAILABLE',
            'processing_time_seconds': elapsed,
            'sentiment_distribution': pd.Series(sent_preds).value_counts().to_dict(),
            'emotion_distribution': pd.Series(emotions).value_counts().to_dict(),
            'embedding_shape': list(all_embeddings.shape),
            'labels': {
                'sentiment': ['positive', 'neutral', 'negative'],
                'emotion': ['joy', 'sadness', 'anger', 'fear', 'surprise', 'neutral']
            },
            'limitations': 'Emotion classification combines neural sentiment priors with lexical affective triggers; ground truth human emotion labels are not present in raw app review export.'
        }

        with open(OUT_REPORT_JSON, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report


def run(verbose: bool = True) -> dict[str, Any]:
    """Runs actual IndoBERT inference pipeline."""
    if verbose:
        print("=" * 60)
        print("03_indobert.py | IndoBERT Neural Feature & Sentiment Inference")
        print("=" * 60)

    in_csv = INPUT_CSV if INPUT_CSV.exists() else FALLBACK_CSV
    df = pd.read_csv(in_csv)

    engine = IndoBERTInferenceEngine()
    report = engine.run_inference(df)

    if verbose:
        print(f"[STATUS]     IndoBERT Status: {report['inference_status']}")
        print(f"[DEVICE]     Accelerated on: {report['device']}")
        print(f"[RECORDS]    Processed {report['number_of_records']} records in {report['processing_time_seconds']}s")
        print("\nSentiment Distribution:")
        for k, v in report['sentiment_distribution'].items():
            print(f"  {k:10s}: {v:4d} ({v/report['number_of_records']*100:.1f}%)")
        print("\nEmotion Distribution:")
        for k, v in report['emotion_distribution'].items():
            print(f"  {k:10s}: {v:4d} ({v/report['number_of_records']*100:.1f}%)")
        print(f"\n✓ 03_indobert.py complete | Embeddings saved: {report['embedding_shape']}")

    return report


if __name__ == "__main__":
    run(verbose=True)
