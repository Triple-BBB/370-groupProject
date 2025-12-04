import pandas as pd
import matplotlib.pyplot as plt
import os

# ------------------------------
# Config
# ------------------------------
INPUT = "data/processed/processed_speeches/tfidf_custom_labels.csv"
OUTPUT_DIR = "data/processed/processed_speeches/tfidf_barplots"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    df = pd.read_csv(INPUT)

    # Ensure correct types
    df["tfidf"] = df["tfidf"].astype(float)

    labels = df["annotation_label"].unique()

    for label in labels:
        subset = df[df["annotation_label"] == label].sort_values("tfidf", ascending=False)[:10]

        plt.figure(figsize=(10, 5))
        plt.barh(subset["word"], subset["tfidf"], color="skyblue")
        plt.xlabel("TF-IDF Score")
        plt.ylabel("Word")
        plt.title(f"Top 10 TF-IDF Words — {label}")
        plt.gca().invert_yaxis()  # highest at top
        plt.tight_layout()

        out_path = os.path.join(OUTPUT_DIR, f"{label}_tfidf_barplot.png")
        plt.savefig(out_path, dpi=200)
        plt.close()

        print(f"Saved → {out_path}")

    print("\n🎉 All barplots generated!")

if __name__ == "__main__":
    main()
