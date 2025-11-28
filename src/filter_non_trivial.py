from pathlib import Path
import csv
import re

INPUT_CSV = Path("data/processed/processed_speeches/final_chars_speeches_cleaned.csv")
OUTPUT_CSV = Path("data/processed/processed_speeches/final_chars_speeches_non_trivial.csv")

# Very small whitelist of "strong" words (you can add/remove)
SPELLS = {
    "obliviate", "expelliarmus", "lumos", "nox", "stupefy",
    "crucio", "imperio", "avadakedavra", "avada", "kedavra",
    "expectopatronum", "expecto", "patronum", "protego",
}

IMPORTANT_TERMS = {
    # main trio
    "harry", "ron", "hermione",

    # key characters
    "dumbledore", "voldemort", "snape", "ginny", "draco",
    "sirius", "lupin", "hagrid", "mcgonagall", "bellatrix",
    "weasley", "malfoy", "neville", "luna",

    # places / groups / objects
    "hogwarts", "ministry", "azkaban", "order", "phoenix",
    "deathly", "hallows", "horcrux", "horcruxes",
    "dementor", "dementors", "muggle", "muggles",
    "auror", "aurors", "deatheater", "deatheaters",
    "wand", "wands", "gryffindor", "slytherin", "hufflepuff", "ravenclaw",
}


def tokenize(text: str):
    # simple word tokenizer: letters + apostrophes
    return re.findall(r"[A-Za-z']+", text)


def has_spell(words):
    return any(w.lower() in SPELLS for w in words)


def contains_important_term(words):
    return any(w.lower() in IMPORTANT_TERMS for w in words)


def is_non_trivial(text: str) -> bool:
    words = tokenize(text)
    word_count = len(words)

    # keep everything with 3+ words
    if word_count >= 3:
        return True

    # for very short lines, keep only if they contain a spell or proper noun
    if has_spell(words):
        return True

    if contains_important_term(words):
        return True

    # otherwise treat as trivial and drop
    return False


def main():
    kept_rows = []

    with INPUT_CSV.open("r", encoding="utf-8", errors="ignore") as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames or ["movie", "character", "speech_id", "text"]

        for row in reader:
            text = (row.get("text") or "").strip()
            if is_non_trivial(text):
                kept_rows.append({
                    "movie": (row.get("movie") or "").strip(),
                    "character": (row.get("character") or "").strip(),
                    "speech_id": (row.get("speech_id") or "").strip(),
                    "text": text,
                })

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=["movie", "character", "speech_id", "text"])
        writer.writeheader()
        writer.writerows(kept_rows)

    print(f"Kept {len(kept_rows)} non-trivial speeches → {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
