import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_PATH = Path("data/processed/processed_speeches/annotation_dataset_RHD_final.csv")
OUT_PNG = Path("data/processed/processed_speeches/topic_distribution_overall.png")

MAIN = {"RON", "HERMIONE", "DUMBLEDORE"}

def main():
    # Load annotated dataset
    df = pd.read_csv(DATA_PATH)

    # Keep only the 3 characters
    df = df[df["character"].str.upper().isin(MAIN)]

    # Count topic frequencies
    topic_counts = df["annotation_label"].value_counts().sort_index()

    # Convert to percentages
    total = topic_counts.sum()
    topic_percent = (topic_counts / total) * 100

    print("\nOverall Topic Distribution (% of all lines):\n")
    print(topic_percent.round(2))

    # Plot
    plt.figure(figsize=(10,6))
    plt.bar(topic_percent.index, topic_percent.values, color="#4C72B0")

    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Percentage of all lines (%)")
    plt.title("Overall Topic Distribution Across Ron, Hermione, and Dumbledore")

    plt.tight_layout()
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_PNG, dpi=300)
    plt.close()

    print(f"\nSaved plot → {OUT_PNG}")

if __name__ == "__main__":
    main()
