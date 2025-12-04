import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ---- Load data ----
df = pd.read_csv("data/processed/processed_speeches/annotation_dataset_RHD_final.csv")

# Clean label text
df["annotation_label"] = df["annotation_label"].str.strip()

# Characters we care about
characters = ["RON", "HERMIONE", "DUMBLEDORE"]

# Topic order
topic_order = ["Danger", "Duty", "Informative", "Magic", "Mockery", "Relationship", "Storyline"]

# ---- Build table: topics x characters = percentage ----
data = []

for topic in topic_order:
    row = {"annotation_label": topic}
    for char in characters:
        subset_char = df[df["character"] == char]
        total_char = len(subset_char)
        if total_char == 0:
            pct = 0.0
        else:
            count_topic = (subset_char["annotation_label"] == topic).sum()
            pct = 100 * count_topic / total_char
        row[char] = pct
    data.append(row)

table = pd.DataFrame(data)

# ---- Plot grouped bar chart ----
x = np.arange(len(topic_order))
width = 0.25

fig, ax = plt.subplots(figsize=(11, 6))

ax.bar(x - width, table["RON"], width, label="RON", color="#4C72B0")
ax.bar(x, table["HERMIONE"], width, label="HERMIONE", color="#55A868")
ax.bar(x + width, table["DUMBLEDORE"], width, label="DUMBLEDORE", color="#C44E52")

ax.set_xticks(x)
ax.set_xticklabels(topic_order, rotation=30, ha="right")

ax.set_ylabel("Percentage of character's lines (%)")
ax.set_xlabel("Topic")
ax.set_title("Topic Distribution per Character (RHD)")
ax.legend()

plt.tight_layout()

# ---- SAVE PLOT ----
output_path = "data/processed/processed_speeches/topic_distribution_RHD.png"
plt.savefig(output_path, dpi=300)
plt.close()

print("\nSaved grouped bar chart to:")
print("   ", output_path)

# ---- Print the table too ----
print("\nPercentage of each character's lines in each topic:\n")
print(table.to_string(index=False))
