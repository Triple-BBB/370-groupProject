import os
import re
import pandas as pd
from collections import defaultdict

# Diagnostic run: replicate parse_script from src/extract_all.py
INPUT_DIR = "data/processed"
TARGET_MOVIES = [
    "Deathly Hallows: Part 1",
    "Deathly Hallows: Part 2",
    "Half-Blood Prince",
    "Prisoner of Azkaban"
]

NAME_PATTERN = re.compile(r"^\s*([A-Z\’\.\-\']+(?:\s+[A-Z\’\.\-\']+){0,4})(?:\s*\(.*\))?\s*$")
SCENE_HEADING_PATTERN = re.compile(r"^\s*(\d+[A-Z]?\s+)?(INT\.|EXT\.|EST\.|I/E\.|TITLE CARD)")
NOISE_PATTERN = re.compile(r"(Rev\.\s\d+|HARRY POTTER.*PT\.|CONTINUED:|FINAL WHITE DRAFT|Warner Bros\.|Screenplay by|^\d+\.$)")
CAMERA_PATTERN = re.compile(r"^\s*(CAMERA|WE\s+SEE|WE\s+PUSH|WE\s+ZOOM|WE\s+FLY|FADE\s+IN:|CUT\s+TO:|DISSOLVE\s+TO:)")


def parse_script(filepath, movie_title):
    extracted_data = []
    char_counters = defaultdict(int)
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    i = 0
    total_lines = len(lines)
    script_started = False

    while i < total_lines:
        line = lines[i].strip()
        if not script_started:
            if "FADE IN" in line or SCENE_HEADING_PATTERN.match(line):
                script_started = True
            else:
                i += 1
                continue

        name_match = NAME_PATTERN.match(line)
        if (name_match and not SCENE_HEADING_PATTERN.match(line)
            and not NOISE_PATTERN.search(line) and not CAMERA_PATTERN.match(line)):
            raw_name = name_match.group(1).strip()
            if raw_name in ["THE END", "FADE OUT", "CUT TO", "DARKNESS", "FADE IN"]:
                i += 1
                continue

            if i + 1 < total_lines:
                dialogue_block = []
                j = i + 1
                while j < total_lines:
                    d_line = lines[j].strip()
                    if d_line == "":
                        break
                    if NAME_PATTERN.match(lines[j]) and not SCENE_HEADING_PATTERN.match(lines[j]):
                        break
                    if SCENE_HEADING_PATTERN.match(lines[j]):
                        break
                    if CAMERA_PATTERN.match(lines[j]):
                        break
                    if NOISE_PATTERN.search(d_line):
                        j += 1
                        break
                    if d_line.startswith(raw_name.title()) or d_line.startswith(raw_name.capitalize()):
                        break
                    if d_line.startswith("She ") or d_line.startswith("He ") or d_line.startswith("They "):
                        break

                    dialogue_block.append(d_line)
                    j += 1

                if dialogue_block:
                    char_counters[raw_name] += 1
                    char_id = f"{raw_name}_{char_counters[raw_name]}"
                    full_dialogue = " ".join(dialogue_block)
                    extracted_data.append({
                        "Movie": movie_title,
                        "Character_ID": char_id,
                        "Line_Index": i + 1,
                        "Dialogue": full_dialogue,
                        "Character": raw_name
                    })
                i = j - 1
        i += 1
    return extracted_data


if __name__ == '__main__':
    files_in_dir = os.listdir(INPUT_DIR)
    print(f"Scanning {INPUT_DIR} (contains {len(files_in_dir)} files)...")

    all_data = []
    per_movie_counts = {}

    for target in TARGET_MOVIES:
        matches = [f for f in files_in_dir if target.lower() in f.lower()]
        if not matches:
            print(f"WARNING: no match for target '{target}'")
            per_movie_counts[target] = 0
            continue
        # If multiple matches, list them
        for match in matches:
            print(f"Processing match for '{target}': {match}")
            full_path = os.path.join(INPUT_DIR, match)
            movie_data = parse_script(full_path, target)
            print(f"  -> extracted {len(movie_data)} dialogue entries from {match}")
            per_movie_counts[target] = per_movie_counts.get(target, 0) + len(movie_data)
            all_data.extend(movie_data)

    print('\nSummary per movie:')
    for k, v in per_movie_counts.items():
        print(f" - {k}: {v}")
    print(f"Total extracted entries: {len(all_data)}")

    df = pd.DataFrame(all_data)
    out_all = 'data/all_characters_dialogue_strict.csv'
    out_sample = 'data/manual_analysis_sample_strict.csv'

    print(f"Writing dataframe to {out_all} (rows: {df.shape[0]}, cols: {df.shape[1] if df.shape[0]>0 else 0})")
    df.to_csv(out_all, index=False)
    print(f"Written {out_all}: size={os.path.getsize(out_all)} bytes")

    if df.shape[0] == 0:
        print('No rows to sample; creating empty sample file instead.')
        pd.DataFrame().to_csv(out_sample, index=False)
        print(f"Written {out_sample}: size={os.path.getsize(out_sample)} bytes")
    else:
        sampled_data = []
        for movie in df['Movie'].unique():
            movie_df = df[df['Movie'] == movie]
            n_sample = min(50, len(movie_df))
            sample = movie_df.sample(n=n_sample, random_state=42)
            sampled_data.append(sample)
        final_sample = pd.concat(sampled_data)
        final_sample.to_csv(out_sample, index=False)
        print(f"Written {out_sample}: size={os.path.getsize(out_sample)} bytes")
