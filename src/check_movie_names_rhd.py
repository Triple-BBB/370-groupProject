from pathlib import Path
import csv
from collections import Counter

INPUT = Path("data/processed/processed_speeches/final_chars_speeches_non_trivial_RHD.csv")

def main():
    movie_counts = Counter()

    with INPUT.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie = (row.get("movie") or "").strip()
            movie_counts[movie] += 1

    print("Distinct movie names and their line counts:\n")
    for movie, count in sorted(movie_counts.items(), key=lambda x: x[0]):
        print(f"{repr(movie)}\t→ {count} lines")

    print(f"\nTotal distinct movies: {len(movie_counts)}")

if __name__ == "__main__":
    main()
