import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/processed_speeches/annotation_dataset_RHD_final.csv")

# Ensure label column is correct
df['annotation_label'] = df['annotation_label'].str.strip()

characters = ["RON", "HERMIONE", "DUMBLEDORE"]

results = {}

for char in characters:
    subset = df[df["character"] == char]

    # Count topics
    counts = subset["annotation_label"].value_counts()

    # Convert to percentage
    perc = (counts / counts.sum()) * 100

    # Save top 3
    results[char] = perc.head(3)

    # --- Plot ---
    plt.figure(figsize=(6,4))
    perc.head(3).plot(kind="bar", color=["#4C72B0", "#55A868", "#C44E52"])
    plt.title(f"Top 3 Topics for {char}")
    plt.ylabel("Percentage of speech (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Print results numerically too
print("\n=== TOP 3 TOPICS PER CHARACTER ===\n")
for char, data in results.items():
    print(f"{char}:")
    for topic, pct in data.items():
        print(f"  {topic:<15} {pct:.2f}%")
    print()
