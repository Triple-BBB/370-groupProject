from pathlib import Path
import csv

INPUT = Path("data/processed/processed_speeches/final_chars_speeches_non_trivial.csv")
OUTPUT = Path("data/processed/processed_speeches/final_chars_speeches_non_trivial_RHD.csv")

TARGET = {"RON", "HERMIONE", "DUMBLEDORE"}

def main():
    kept = []

    with INPUT.open("r", encoding="utf-8", errors="ignore") as f_in:
        reader = csv.DictReader(f_in)
        for row in reader:
            character = (row.get("character") or "").strip()
            if character in TARGET:
                kept.append({
                    "movie": row.get("movie", "").strip(),
                    "character": character,
                    "speech_id": row.get("speech_id", "").strip(),
                    "text": row.get("text", "").strip(),
                })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=["movie", "character", "speech_id", "text"])
        writer.writeheader()
        writer.writerows(kept)

    print(f"Saved {len(kept)} lines → {OUTPUT}")

if __name__ == "__main__":
    main()
