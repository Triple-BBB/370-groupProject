from pathlib import Path
import csv
import random
import math
from collections import Counter, defaultdict

INPUT = Path("data/processed/processed_speeches/final_chars_speeches_non_trivial_RHD.csv")
OUTPUT = Path("data/processed/processed_speeches/open_coding_sample_RHD_100.csv")

TOTAL_SAMPLE_SIZE = 100
TARGET_CHARACTERS = {"RON", "HERMIONE", "DUMBLEDORE"}

random.seed(42)  # reproducible sampling


def largest_remainder_quota(total_size, counts_dict):
    """
    Given total_size (e.g. 100) and counts_dict = {key: count},
    return an integer quota per key whose sum = total_size,
    using largest remainder method.
    """
    total = sum(counts_dict.values())
    if total == 0:
        return {k: 0 for k in counts_dict}

    # raw fractional quotas
    raw = {k: (count * total_size) / total for k, count in counts_dict.items()}
    base = {k: int(math.floor(v)) for k, v in raw.items()}
    remainder = {k: raw[k] - base[k] for k in counts_dict}

    current_sum = sum(base.values())
    remaining = total_size - current_sum

    # give leftover slots to highest remainders
    for k, _ in sorted(remainder.items(), key=lambda x: x[1], reverse=True):
        if remaining <= 0:
            break
        base[k] += 1
        remaining -= 1

    return base


def main():
    # 1) Read all rows (they should already be only R/H/D, but we enforce it)
    rows = []
    with INPUT.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            character = (row.get("character") or "").strip()
            if character in TARGET_CHARACTERS:
                rows.append({
                    "movie": (row.get("movie") or "").strip(),
                    "character": character,
                    "speech_id": (row.get("speech_id") or "").strip(),
                    "text": (row.get("text") or "").strip(),
                })

    if not rows:
        print("No rows found for target characters. Check input file / path.")
        return

    print(f"Total lines for R/H/D = {len(rows)}")

    # 2) Movie-level quotas (how many lines each movie gets out of 100)
    movie_counts = Counter(r["movie"] for r in rows)
    movie_quota = largest_remainder_quota(TOTAL_SAMPLE_SIZE, movie_counts)
    print("Movie quotas:", movie_quota)

    # 3) Within each movie, character-level quotas (Ron/Hermione/Dumbledore)
    sample_rows = []

    # group by movie
    rows_by_movie = defaultdict(list)
    for r in rows:
        rows_by_movie[r["movie"]].append(r)

    for movie, movie_rows in rows_by_movie.items():
        m_quota = movie_quota.get(movie, 0)
        if m_quota == 0:
            continue

        # counts per character inside that movie
        char_counts = Counter(r["character"] for r in movie_rows)
        char_quota = largest_remainder_quota(m_quota, char_counts)
        print(f"{movie}: char quotas = {char_quota}")

        # group rows by character for this movie
        by_char = defaultdict(list)
        for r in movie_rows:
            by_char[r["character"]].append(r)

        # sample per character
        for char, cq in char_quota.items():
            if cq <= 0:
                continue
            pool = by_char.get(char, [])
            if not pool:
                continue

            k = min(cq, len(pool))  # just in case there are fewer lines than desired
            sample = random.sample(pool, k)
            sample_rows.extend(sample)

    # 4) Safety: enforce at most 100 rows, adjust if rounding caused off-by-1
    if len(sample_rows) > TOTAL_SAMPLE_SIZE:
        sample_rows = random.sample(sample_rows, TOTAL_SAMPLE_SIZE)
    elif len(sample_rows) < TOTAL_SAMPLE_SIZE:
        print(f"Warning: only {len(sample_rows)} lines sampled (not enough data).")

    # 5) Write output CSV
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["movie", "character", "speech_id", "text"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in sample_rows:
            writer.writerow(r)

    print(f"Wrote {len(sample_rows)} sampled lines to {OUTPUT}")


if __name__ == "__main__":
    main()
