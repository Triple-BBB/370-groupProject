from pathlib import Path
import csv

INPUT = Path("data/processed/processed_speeches/final_chars_speeches_non_trivial_RHD.csv")
OUTPUT = Path("data/processed/processed_speeches/final_chars_speeches_non_trivial_RHD_normalized.csv")

NAME_MAP = {
    "phoenix": "the_order_phoenix",
    "deathly_hallows_part2_all_speeches": "deathly_hallows_part2",
    "goblet_of_fire_all_speeches": "goblet_of_fire",
    "half_blood_prince_all_speeches": "half_blood_prince",
    "prisoner_azkaban_all_speeches": "prisoner_azkaban",
    "sorcerer_s_stone_all_characters": "sorcerer_s_stone",
    "chamber_of_secrets_speeches": "chamber_of_secrets",
}

def main():
    rows = []

    with INPUT.open("r", encoding="utf-8", errors="ignore") as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames or ["movie", "character", "speech_id", "text"]

        for row in reader:
            movie = (row.get("movie") or "").strip()
            normalized = NAME_MAP.get(movie, movie)  # map if in dict, else keep as is

            rows.append({
                "movie": normalized,
                "character": (row.get("character") or "").strip(),
                "speech_id": (row.get("speech_id") or "").strip(),
                "text": (row.get("text") or "").strip(),
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=["movie", "character", "speech_id", "text"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote normalized file → {OUTPUT}")

if __name__ == "__main__":
    main()
