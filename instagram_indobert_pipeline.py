"""
Pipeline: Analisis Topik Percakapan Instagram Indonesia dengan IndoBERT + BERTopic
Target: Naskah jurnal Scopus Q1

Alur:
1. Load data (komentar/caption Instagram, kolom minimal: 'text')
2. Preprocessing teks informal Bahasa Indonesia
3. Ekstraksi embedding dengan IndoBERT
4. Topic modeling dengan BERTopic (di atas embedding IndoBERT)
5. Baseline pembanding: LDA klasik
6. Evaluasi (topic coherence) & ekspor hasil

Install dependencies:
    pip install transformers torch bertopic sentence-transformers \
        scikit-learn gensim pandas emoji Sastrawi --break-system-packages
"""

import re
import emoji
import torch
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModel
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory


# =========================================================
# 1. KONFIGURASI
# =========================================================
MODEL_NAME = "indobenchmark/indobert-base-p1"   # ganti ke -p2 / -large-p2 sesuai kebutuhan
INPUT_CSV = "data/Review Instagram.csv"
OUTPUT_DIR = "output/"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Kamus normalisasi slang minimal (silakan diperluas / ganti dengan kamus slang ID yang lebih lengkap,
# mis. dari Colloquial Indonesian Lexicon)
SLANG_DICT = {
    "gk": "tidak", "ga": "tidak", "gak": "tidak", "yg": "yang",
    "utk": "untuk", "dgn": "dengan", "krn": "karena", "aja": "saja",
    "bgt": "banget", "sm": "sama", "jd": "jadi", "udh": "sudah",
    "blm": "belum", "tp": "tapi", "dr": "dari", "dpt": "dapat",
}

stopword_factory = StopWordRemoverFactory()
stopword_remover = stopword_factory.create_stop_word_remover()


# =========================================================
# 2. PREPROCESSING
# =========================================================
def clean_text(text: str) -> str:
    """Bersihkan teks komentar/caption Instagram: url, mention, hashtag, emoji, slang, simbol."""
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)          # URL
    text = re.sub(r"@\w+", " ", text)                       # mention
    text = re.sub(r"#(\w+)", r"\1", text)                    # hashtag -> keep kata, buang '#'
    text = emoji.replace_emoji(text, replace=" ")            # emoji dibuang (opsional: replace_emoji ke label)
    text = re.sub(r"[^a-z\s]", " ", text)                    # buang angka & simbol
    text = re.sub(r"\s+", " ", text).strip()

    # normalisasi slang
    words = text.split()
    words = [SLANG_DICT.get(w, w) for w in words]
    text = " ".join(words)

    # stopword removal (pakai Sastrawi; bisa dimatikan kalau ingin BERTopic pegang stopword sendiri)
    text = stopword_remover.remove(text)

    return text.strip()


def preprocess_dataframe(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    df["clean_text"] = df[text_col].apply(clean_text)
    df = df[df["clean_text"].str.len() > 3].reset_index(drop=True)  # buang teks terlalu pendek
    return df


# =========================================================
# 3. EKSTRAKSI EMBEDDING DENGAN INDOBERT
# =========================================================
class IndoBERTEmbedder:
    def __init__(self, model_name: str = MODEL_NAME, device: str = DEVICE):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(device)
        self.model.eval()
        self.device = device

    @torch.no_grad()
    def encode(self, texts, batch_size: int = 16, max_length: int = 128) -> np.ndarray:
        """Mean-pooling atas last_hidden_state sebagai representasi kalimat."""
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = self.tokenizer(
                batch, padding=True, truncation=True,
                max_length=max_length, return_tensors="pt"
            ).to(self.device)

            output = self.model(**enc)
            token_embeddings = output.last_hidden_state          # (B, T, H)
            mask = enc["attention_mask"].unsqueeze(-1).float()   # (B, T, 1)

            summed = (token_embeddings * mask).sum(dim=1)
            counted = mask.sum(dim=1).clamp(min=1e-9)
            mean_pooled = summed / counted                        # (B, H)

            all_embeddings.append(mean_pooled.cpu().numpy())

        return np.vstack(all_embeddings)


# =========================================================
# 4. TOPIC MODELING DENGAN BERTOPIC (di atas embedding IndoBERT)
# =========================================================
def run_bertopic(texts, embeddings, language_stopwords=None, nr_topics="auto"):
    vectorizer_model = CountVectorizer(
        stop_words=language_stopwords, ngram_range=(1, 2), min_df=3
    )

    topic_model = BERTopic(
        embedding_model=None,          # embedding sudah disediakan manual
        vectorizer_model=vectorizer_model,
        nr_topics=nr_topics,
        calculate_probabilities=False,
        verbose=True,
    )

    topics, probs = topic_model.fit_transform(texts, embeddings=embeddings)
    return topic_model, topics, probs


# =========================================================
# 5. BASELINE: LDA KLASIK (PEMBANDING)
# =========================================================
def run_lda_baseline(texts, num_topics: int = 10):
    from gensim import corpora
    from gensim.models import LdaModel

    tokenized = [t.split() for t in texts]
    dictionary = corpora.Dictionary(tokenized)
    dictionary.filter_extremes(no_below=3, no_above=0.5)
    corpus = [dictionary.doc2bow(t) for t in tokenized]

    lda_model = LdaModel(
        corpus=corpus, id2word=dictionary, num_topics=num_topics,
        random_state=42, passes=10
    )
    return lda_model, dictionary, corpus


def compute_coherence(model, texts, dictionary, corpus, model_type="lda"):
    from gensim.models import CoherenceModel

    tokenized = [t.split() for t in texts]
    if model_type == "lda":
        topics = [
            [word for word, _ in model.show_topic(i, topn=10)]
            for i in range(model.num_topics)
        ]
    else:
        raise NotImplementedError("Untuk BERTopic, ambil topik via topic_model.get_topics()")

    coherence_model = CoherenceModel(
        topics=topics, texts=tokenized, dictionary=dictionary, coherence="c_v"
    )
    return coherence_model.get_coherence()


# =========================================================
# 6. MAIN PIPELINE
# =========================================================
def main():
    print(f"[INFO] Device: {DEVICE}")

    # --- Load data ---
    df = pd.read_csv(INPUT_CSV)
    print(f"[INFO] Data awal: {len(df)} baris")

    # --- Preprocessing ---
    df = preprocess_dataframe(df, text_col="Review Text")
    texts = df["clean_text"].tolist()
    print(f"[INFO] Data setelah preprocessing: {len(texts)} baris")

    # --- Embedding IndoBERT ---
    print("[INFO] Memuat IndoBERT & mengekstrak embedding...")
    embedder = IndoBERTEmbedder()
    embeddings = embedder.encode(texts)
    print(f"[INFO] Shape embedding: {embeddings.shape}")

    # --- BERTopic + IndoBERT ---
    print("[INFO] Menjalankan BERTopic...")
    topic_model, topics, probs = run_bertopic(texts, embeddings)
    df["topic"] = topics

    topic_info = topic_model.get_topic_info()
    print("[INFO] Ringkasan topik teratas:")
    print(topic_info.head(15))

    # --- Simpan hasil ---
    df.to_csv(f"{OUTPUT_DIR}hasil_topik_instagram.csv", index=False)
    topic_info.to_csv(f"{OUTPUT_DIR}ringkasan_topik.csv", index=False)
    topic_model.save(f"{OUTPUT_DIR}bertopic_model")

    # --- Baseline LDA (opsional, untuk perbandingan di naskah) ---
    print("[INFO] Menjalankan baseline LDA...")
    lda_model, dictionary, corpus = run_lda_baseline(texts, num_topics=len(topic_info) - 1 or 10)
    lda_coherence = compute_coherence(lda_model, texts, dictionary, corpus, model_type="lda")
    print(f"[INFO] LDA coherence (c_v): {lda_coherence:.4f}")

    print("[DONE] Pipeline selesai. Hasil tersimpan di folder output/.")


if __name__ == "__main__":
    main()
