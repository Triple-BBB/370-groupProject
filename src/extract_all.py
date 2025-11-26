import os
import re
import pandas as pd
from collections import defaultdict

# ==========================================
# 1. CONFIGURATION
# ==========================================

INPUT_DIR = "data/processed"

# RESTORED TO FULL NAMES
# The script will use these specific strings for the "Movie" column in your CSV.
TARGET_MOVIES = [
    "Harry Potter and the Deathly Hallows: Part 1",
    "Harry Potter and the Deathly Hallows: Part 2",
    "Harry Potter and the Half-Blood Prince",
    "Harry Potter and the Prisoner of Azkaban",
    "Harry Potter and the Order of the Phoenix"
]

# ==========================================
# 2. PATTERNS
# ==========================================

NAME_PATTERN = re.compile(r"^\s*([A-Z\’\.\-\']+(?:\s+[A-Z\’\.\-\']+){0,4})(?:\s*\(.*\))?\s*$")
SCENE_HEADING_PATTERN = re.compile(r"^\s*(\d+[A-Z]?\s+)?(INT\.|EXT\.|EST\.|I/E\.|TITLE CARD)")
NOISE_PATTERN = re.compile(r"(Rev\.\s\d+|HARRY POTTER.*PT\.|CONTINUED:|FINAL WHITE DRAFT|Warner Bros\.|Screenplay by|^\d+\.$)")
CAMERA_PATTERN = re.compile(r"^\s*(CAMERA|WE\s+SEE|WE\s+PUSH|WE\s+ZOOM|WE\s+FLY|FADE\s+IN:|CUT\s+TO:|DISSOLVE\s+TO:)")

# Action Names Watchlist
ACTION_NAMES = [
    "Harry", "Ron", "Hermione", "Snape", "Dumbledore", "Voldemort", 
    "Hagrid", "Draco", "Ginny", "Arthur", "Molly", "Bellatrix", 
    "Lucius", "Sirius", "Lupin", "Fred", "George", "Neville", "Luna"
]

# ==========================================
# 3. EXTRACTION LOGIC
# ==========================================

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
        
        if (name_match and 
            not SCENE_HEADING_PATTERN.match(line) and 
            not NOISE_PATTERN.search(line) and
            not CAMERA_PATTERN.match(line)):
            
            raw_name = name_match.group(1).strip()
            
            if raw_name in ["THE END", "FADE OUT", "CUT TO", "DARKNESS", "FADE IN"]:
                i += 1
                continue

            if i + 1 < total_lines:
                dialogue_block = []
                j = i + 1
                
                while j < total_lines:
                    d_line = lines[j].strip()
                    
                    if d_line == "": break
                    if NAME_PATTERN.match(lines[j]) and not SCENE_HEADING_PATTERN.match(lines[j]): break
                    if SCENE_HEADING_PATTERN.match(lines[j]) or CAMERA_PATTERN.match(lines[j]): break
                    if NOISE_PATTERN.search(d_line):
                        j += 1
                        break

                    # Action Checks
                    if d_line.startswith(raw_name.title()) or d_line.startswith(raw_name.capitalize()): break
                    if d_line.startswith("She ") or d_line.startswith("He ") or d_line.startswith("They "): break

                    # Punctuation/Name Check
                    first_word_raw = d_line.split(' ')[0]
                    first_word_clean = first_word_raw.strip('.,?!')

                    if first_word_clean in ACTION_NAMES:
                        name_len = len(first_word_clean)
                        if len(d_line) > name_len:
                            next_char = d_line[name_len]
                            if next_char in [',', '?', '!', ':', ';']: pass
                            elif next_char == ' ': break
                            elif next_char == "'": break

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

# ==========================================
# 4. EXECUTION
# ==========================================

all_data = []
files_in_dir = os.listdir(INPUT_DIR)

print(f"Scanning {INPUT_DIR}...")

for target in TARGET_MOVIES:
    # 1. Try exact match
    match = next((f for f in files_in_dir if target.lower() in f.lower()), None)
    
    # 2. If no exact match, try swapping colon for dash (common Windows/Git rename issue)
    if not match:
        target_variant = target.replace(":", "-")
        match = next((f for f in files_in_dir if target_variant.lower() in f.lower()), None)

    if match:
        print(f"Processing: {match} -> AS -> {target}")
        full_path = os.path.join(INPUT_DIR, match)
        movie_data = parse_script(full_path, target)
        all_data.extend(movie_data)
    else:
        print(f"WARNING: Could not find file for {target}")

df = pd.DataFrame(all_data)

# Save ALL
df.to_csv("data/all_characters_dialogue_v6.csv", index=False)
print("Saved: data/all_characters_dialogue_v6.csv")

# Save SAMPLE
sampled_data = []
for movie in df['Movie'].unique():
    movie_df = df[df['Movie'] == movie]
    n_sample = min(50, len(movie_df))
    sample = movie_df.sample(n=n_sample, random_state=42)
    sampled_data.append(sample)

final_sample = pd.concat(sampled_data)
final_sample.to_csv("data/manual_analysis_sample_v6.csv", index=False)
print("Saved: data/manual_analysis_sample_v6.csv")