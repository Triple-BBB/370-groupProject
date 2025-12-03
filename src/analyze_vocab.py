import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

DATA_PATH = "data/processed/processed_speeches/annotation_dataset_RHD_final.csv"

def main():
    # --------- load data ----------
    df = pd.read_csv(DATA_PATH)

    assert "text" in df.columns, "Expected a 'text' column"
    texts = df["text"].astype(str).tolist()
    print(f"Loaded {len(texts)} annotated lines.")

    # --------- build raw vocabulary ----------
    # CountVectorizer instead of Tfidf, no max_features limit
    cv = CountVectorizer(
        stop_words="english",
        lowercase=True
    )
    X = cv.fit_transform(texts)
    vocab = cv.get_feature_names_out()
    term_counts = X.toarray().sum(axis=0)  # total count across all docs

    print(f"\nTotal unique tokens (after lowercasing + English stopword removal): {len(vocab)}")

    # Build a Counter of word -> frequency
    freq = Counter(dict(zip(vocab, term_counts)))

    # how many words appear once, 2–5 times, >5 times
    once = sum(1 for c in freq.values() if c == 1)
    two_to_five = sum(1 for c in freq.values() if 2 <= c <= 5)
    more_than_five = sum(1 for c in freq.values() if c > 5)

    print(f"\nFrequency breakdown:")
    print(f"  Hapax (appear once):           {once}")
    print(f"  Appear 2–5 times:              {two_to_five}")
    print(f"  Appear more than 5 times:      {more_than_five}")

    # top 30 most frequent words
    print("\nTop 30 most frequent tokens:")
    for word, c in freq.most_common(30):
        print(f"  {word:20s} {c}")

    # --------- coverage for some max_features choices ----------
    # sort terms by frequency descending
    sorted_terms = [w for w, _ in freq.most_common()]
    total_tokens = sum(freq.values())

    def coverage_at_k(k):
        kept_terms = sorted_terms[:k]
        kept_count = sum(freq[w] for w in kept_terms)
        return kept_count / total_tokens * 100

    for k in [2000, 5000, 8000]:
        if k <= len(sorted_terms):
            cov = coverage_at_k(k)
            print(f"\nIf you keep top {k} words, you cover about {cov:.2f}% of all token occurrences.")

    # --------- OPTIONAL: build a TF-IDF model with no max_features ----------
    # This is just to confirm it runs; you can still add max_features later.
    print("\nFitting a TF-IDF model with full vocabulary (no max_features)...")
    tfidf_vec = TfidfVectorizer(
        stop_words="english",
        lowercase=True
    )
    tfidf_matrix = tfidf_vec.fit_transform(texts)
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}  (docs x vocab_size)")

if __name__ == "__main__":
    main()
