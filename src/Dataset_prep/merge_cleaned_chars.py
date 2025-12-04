from pathlib import Path
import csv

# Folder with manually cleaned files
MANUAL_DIR = Path("data/processed/processed_speeches/manually-clean")

# Dumbledore cleaned CSV (in the same folder)
DUMBLEDORE_CSV = MANUAL_DIR / "dumbledore_all_movies_manual_clean.csv"

# Final merged output
OUTPUT_CSV = Path("data/processed/processed_speeches/final_chars_speeches_cleaned.csv")

FIELDNAMES = ["movie", "character", "speech_id", "text"]


def collect_from_manual_dir():
    rows = []

    # only the *_four_chars.tsv files (other characters)
    for tsv_path in MANUAL_DIR.glob("*_four_chars.tsv"):
        movie_raw = tsv_path.stem              # e.g. "half_blood_prince_four_chars"
        movie_name = movie_raw.replace("_four_chars", "")  # "half_blood_prince"

        with tsv_path.open("r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                rows.append({
                    "movie": movie_name,
                    "character": row.get("character", "").strip(),
                    "speech_id": row.get("speech_id", "").strip(),
                    "text": row.get("text", "").strip(),
                })

    return rows


def collect_dumbledore():
    rows = []
    with DUMBLEDORE_CSV.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                "movie": row.get("movie", "").strip(),
                "character": row.get("character", "").strip(),
                "speech_id": row.get("speech_id", "").strip(),
                "text": row.get("text", "").strip(),
            })
    return rows


def main():
    all_rows = []

    # 1) all other cleaned characters (from TSVs)
    all_rows.extend(collect_from_manual_dir())

    # 2) add Dumbledore (from CSV)
    all_rows.extend(collect_dumbledore())

    # write final merged CSV
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Wrote {len(all_rows)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
