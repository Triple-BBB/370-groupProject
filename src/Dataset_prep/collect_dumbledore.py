from pathlib import Path
import csv

INPUT_DIR = Path("data/processed/processed_speeches/processed_speeches_all_chars")
OUTPUT_CSV = Path("data/processed/processed_speeches/dumbledore_all_movies.csv")

def main():
    rows = []

    # loop over all .tsv files with all characters
    for tsv_path in INPUT_DIR.glob("*.tsv"):
        movie_name = tsv_path.stem  # use file name as movie id

        with tsv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                char_raw = row.get("character", "")
                char_upper = char_raw.upper()

                # keep any character that contains DUMBLEDORE
                if "DUMBLEDORE" in char_upper:
                    rows.append({
                        "movie": movie_name,
                        "character": char_raw,
                        "speech_id": row.get("speech_id", ""),
                        "text": row.get("text", "").replace("\n", " ").strip(),
                    })

    # write combined CSV
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["movie", "character", "speech_id", "text"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Collected {len(rows)} Dumbledore speeches into {OUTPUT_CSV}")


if __name__ == "__main__":
    main()