import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# ---------------------------------------------------------
# Load the final annotated dataset
# ---------------------------------------------------------
df = pd.read_csv(
    "data/processed/processed_speeches/annotation_dataset_RHD_final.csv"
)

# Sanity checks
assert "annotation_label" in df.columns
assert "text" in df.columns

# ---------------------------------------------------------
# Combine all text per label into a single big document
# ---------------------------------------------------------
label_docs = (
    df.groupby("annotation_label")["text"]
      .apply(lambda x: " ".join(x))
      .to_dict()
)

labels = list(label_docs.keys())
documents = list(label_docs.values())

# ---------------------------------------------------------
# Compute TF-IDF (full vocabulary, stopwords removed)
# ---------------------------------------------------------
vectorizer = TfidfVectorizer(
    stop_words="english",
    lowercase=True
)

tfidf_matrix = vectorizer.fit_transform(documents)
feature_names = vectorizer.get_feature_names_out()

# ---------------------------------------------------------
# Extract TOP 10 TF-IDF words per annotation_label
# ---------------------------------------------------------
results = {}

for i, label in enumerate(labels):
    row = tfidf_matrix[i].toarray()[0]
    top_idx = row.argsort()[-10:][::-1]  # highest → lowest
    top_terms = [(feature_names[idx], float(row[idx])) for idx in top_idx]
    results[label] = top_terms

# ---------------------------------------------------------
# Print readable output
# ---------------------------------------------------------
for label, words in results.items():
    print(f"\n=== TOP 10 TF-IDF WORDS FOR LABEL: {label} ===")
    for term, score in words:
        print(f"{term:20s}  {score:.4f}")

# ---------------------------------------------------------
# Save results to CSV
# ---------------------------------------------------------
rows = []
for label, words in results.items():
    for term, score in words:
        rows.append({
            "annotation_label": label,
            "word": term,
            "tfidf_score": score
        })

out_df = pd.DataFrame(rows)
out_df.to_csv(
    "data/processed/processed_speeches/tfidf_top_words_per_label.csv",
    index=False
)

print("\nSaved → data/processed/processed_speeches/tfidf_top_words_per_label.csv")
