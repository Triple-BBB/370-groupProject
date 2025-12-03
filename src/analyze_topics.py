import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

DATA_PATH = "data/processed/processed_speeches/annotation_dataset_RHD_final.csv"

def main():
    df = pd.read_csv(DATA_PATH)
    
    texts = df["text"].astype(str)
    labels = df["annotation_label"].astype(str)
    
    vectorizer = TfidfVectorizer(stop_words="english", lowercase=True)
    tfidf = vectorizer.fit_transform(texts)
    vocab = np.array(vectorizer.get_feature_names_out())
    
    categories = sorted(labels.unique())
    
    print("\n===== TOP 10 TF-IDF WORDS PER CATEGORY =====\n")
    for cat in categories:
        idx = df.index[df["annotation_label"] == cat]
        submatrix = tfidf[idx].toarray()
        
        mean_tfidf = submatrix.mean(axis=0)
        top10_idx = mean_tfidf.argsort()[::-1][:10]
        
        print(f"\nCategory: {cat}")
        for w, score in zip(vocab[top10_idx], mean_tfidf[top10_idx]):
            print(f"  {w:20s} {score:.4f}")

if __name__ == "__main__":
    main()
