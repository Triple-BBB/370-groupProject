import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

INPUT = "data/processed/processed_speeches/tfidf_custom_labels.csv"
OUTPUT = "data/processed/processed_speeches/tfidf_heatmap_all_labels.png"

TOP_K = 10  # top words per label

def main():
    df = pd.read_csv(INPUT)
    df["tfidf"] = df["tfidf"].astype(float)

    labels = sorted(df["annotation_label"].unique())

    # 1) pick top-K words per label
    top_words_per_label = {}
    for label in labels:
        sub = df[df["annotation_label"] == label].sort_values("tfidf", ascending=False)
        top_words_per_label[label] = list(sub["word"].head(TOP_K))

    # 2) union of all selected words
    vocab = sorted(set(w for words in top_words_per_label.values() for w in words))

    # 3) build matrix: rows = labels, cols = vocab, values = tfidf
    mat = np.zeros((len(labels), len(vocab)))

    for i, label in enumerate(labels):
        sub = df[df["annotation_label"] == label]
        scores = dict(zip(zip(sub["annotation_label"], sub["word"]), sub["tfidf"]))
        for j, w in enumerate(vocab):
            mat[i, j] = scores.get((label, w), 0.0)  # 0 if word not in that label

    # 4) plot heatmap
    plt.figure(figsize=(1.2 * len(vocab), 0.6 * len(labels) + 2))

    im = plt.imshow(mat, aspect="auto", cmap="viridis")

    plt.colorbar(im, label="TF-IDF")

    plt.xticks(ticks=range(len(vocab)), labels=vocab, rotation=90)
    plt.yticks(ticks=range(len(labels)), labels=labels)

    plt.title("Top TF-IDF Words per Annotation Label")
    plt.tight_layout()

    plt.savefig(OUTPUT, dpi=200)
    plt.close()

    print("Saved heatmap →", OUTPUT)

if __name__ == "__main__":
    main()
