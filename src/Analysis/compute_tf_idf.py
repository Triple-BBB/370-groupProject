import pandas as pd
import numpy as np
from collections import Counter
import math

INPUT = "data/processed/processed_speeches/annotation_dataset_RHD_final.csv"
OUTPUT = "data/processed/processed_speeches/tfidf_custom_labels.csv"

def tokenize(text):
    # basic tokenization — you can improve later
    return [
        w.lower()
        for w in text.replace(".", " ").replace(",", " ").split()
        if w.strip()
    ]

def main():
    df = pd.read_csv(INPUT)

    print(f"Loaded {len(df)} annotated lines.")

    # -------------------------------
    # GROUP TEXT BY LABEL (TYPE)
    # -------------------------------
    grouped = df.groupby("annotation_label")["text"].apply(list)
    labels = grouped.index.tolist()
    num_types = len(labels)

    # store all tokens per label
    tokens_by_label = {}
    for label in labels:
        combined = " ".join(grouped[label])
        tokens = tokenize(combined)
        tokens_by_label[label] = tokens

    # -------------------------------
    # COMPUTE TF
    # -------------------------------
    tf = {}  # tf[label][word] = value

    for label, tokens in tokens_by_label.items():
        total_words = len(tokens)
        counts = Counter(tokens)
        tf[label] = {
            word: counts[word] / total_words
            for word in counts
        }

    # -------------------------------
    # COMPUTE IDF
    # -------------------------------
    # Determine in which labels each word appears
    word_in_labels = {}

    for label, tokens in tokens_by_label.items():
        unique_words = set(tokens)
        for w in unique_words:
            word_in_labels.setdefault(w, set()).add(label)

    idf = {}
    for w, label_set in word_in_labels.items():
        df_word = len(label_set)
        idf[w] = math.log(num_types / df_word)

    # -------------------------------
    # COMPUTE TF-IDF
    # -------------------------------
    results = []

    for label in labels:
        for w, tf_value in tf[label].items():
            tfidf = tf_value * idf[w]
            results.append({
                "annotation_label": label,
                "word": w,
                "tf": tf_value,
                "idf": idf[w],
                "tfidf": tfidf
            })

    tfidf_df = pd.DataFrame(results)

    # -------------------------------
    # EXTRACT TOP 10 WORDS PER LABEL
    # -------------------------------
    top_rows = []

    for label in labels:
        subset = tfidf_df[tfidf_df["annotation_label"] == label]
        top = subset.sort_values("tfidf", ascending=False).head(10)
        top_rows.extend(top.to_dict(orient="records"))

    out_df = pd.DataFrame(top_rows)
    out_df.to_csv(OUTPUT, index=False)

    print("\nSaved →", OUTPUT)
    print("Done.")

if __name__ == "__main__":
    main()
