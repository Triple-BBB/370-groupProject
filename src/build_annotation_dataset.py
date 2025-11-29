from pathlib import Path
import csv
import random
import math
from collections import defaultdict, Counter

INPUT = Path(
    "data/processed/processed_speeches/cleaned_non_trivial_RHD/final_chars_speeches_non_trivial_RHD_normalized.csv"
)
OUTPUT = Path(
    "data/processed/processed_speeches/annotation_dataset_RHD.csv"
)

TARGET_RON = 300
TARGET_HERMIONE = 300
CHAR_RON = "RON"
CHAR_HERMIONE = "HERMIONE"
CHAR_DUMBLEDORE = "DUMBLEDORE"

random.seed(42)  # reproducible

def largest_remainder_quota(total_size, counts_dict):
    """
    Given total_size (e.g. 300) and counts_dict = {key: count},
    return an integer quota per key whose sum = total_size,
    using largest remainder method.
    """
    total = sum(counts_dict.values())
    if total == 0:
        return {k: 0 for k in counts_dict}

    raw = {k: (count * total_size) / total for k, count in counts_dict.items()}
    base = {k: int(math.floor(v)) for k, v in raw.items()}
    remainder = {k: raw[k] - base[k] for k in counts_dict}

    current_sum = sum(base.values())
    remaining = total_size - current_sum

    for k, _ in sorted(remainder.items(), key=lambda x: x[1], reverse=True):
        if remaining <= 0:
            break
        base[k] += 1
        remaining -= 1

    return base

def stratified_sample_by_movie(char_rows, target_n):
    """
    char_rows: list of rows (all for a single character).
    target_n: desired sample size (e.g. 300).
    Stratify by movie proportionally, then sample randomly within each movie.
    """
    if not char_rows:
        return []

    # group by movie
    rows_by_movie = defaultdict(list)
    for r in char_rows:
        rows_by_movie[r["movie"]].append(r)

    movie_counts = {m: len(v) for m, v in rows_by_movie.items()}
    quotas = largest_remainder_quota(target_n, movie_counts)

    sampled = []
    leftover_pool = []

    # first pass: respect quotas, but cap at available rows
    for movie, rows_m in rows_by_movie.items():
        q = quotas.get(movie, 0)
        if q <= 0:
            # all rows go to leftover pool (not sampled yet)
            leftover_pool.extend(rows_m)
            continue

        if q >= len(rows_m):
            # we want more than or equal to available rows: take all, nothing leftover
            sampled.extend(rows_m)
        else:
            # sample q, leftover goes to pool
            chosen = random.sample(rows_m, q)
            sampled.extend(chosen)

            remaining = [r for r in rows_m if r not in chosen]
            leftover_pool.extend(remaining)

    # if we undershot the target (because some movies had fewer rows than their quota),
    # top up from leftover_pool
    if len(sampled) < target_n and leftover_pool:
        needed = target_n - len(sampled)
        extra = min(needed, len(leftover_pool))
        sampled.extend(random.sample(leftover_pool, extra))

    # if for some reason we overshoot (shouldn't happen, but safe guard)
    if len(sampled) > target_n:
        sampled = random.sample(sampled, target_n)

    return sampled

def main():
    rows = []

    with INPUT.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "movie": (row.get("movie") or "").strip(),
                "character": (row.get("character") or "").strip(),
                "speech_id": (row.get("speech_id") or "").strip(),
                "text": (row.get("text") or "").strip(),
            })

    # split by character
    dumbledore_rows = [r for r in rows if r["character"] == CHAR_DUMBLEDORE]
    ron_rows = [r for r in rows if r["character"] == CHAR_RON]
    hermione_rows = [r for r in rows if r["character"] == CHAR_HERMIONE]

    print(f"Dumbledore total lines: {len(dumbledore_rows)}")
    print(f"Ron total lines: {len(ron_rows)}")
    print(f"Hermione total lines: {len(hermione_rows)}")

    # stratified sampling for Ron and Hermione
    ron_sample = stratified_sample_by_movie(ron_rows, TARGET_RON)
    hermione_sample = stratified_sample_by_movie(hermione_rows, TARGET_HERMIONE)

    print(f"Ron sampled: {len(ron_sample)}")
    print(f"Hermione sampled: {len(hermione_sample)}")

    # build final annotation set: all Dumbledore + sampled Ron + sampled Hermione
    final_rows = []

    # keep grouped by character (Dumbledore, then Ron, then Hermione)
    for r in dumbledore_rows:
        final_rows.append(r)
    for r in ron_sample:
        final_rows.append(r)
    for r in hermione_sample:
        final_rows.append(r)

    # assign annotation_id
    for idx, r in enumerate(final_rows, start=1):
        r["annotation_id"] = idx
        r["annotation_label"] = ""  # empty column for you to fill in manually

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as f_out:
        fieldnames = ["annotation_id", "movie", "character", "speech_id", "text", "annotation_label"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)

    print(f"Annotation dataset written to: {OUTPUT}")
    print(f"Total rows in annotation file: {len(final_rows)}")


if __name__ == "__main__":
    main()