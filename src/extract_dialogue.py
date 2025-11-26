import os
import re
import pandas as pd
import random

# ==========================================
# 1. CONFIGURATION
# ==========================================

# Directory containing your processed text files
INPUT_DIR = "data/processed"

# Target files (Partial matches for filenames)
TARGET_MOVIES = [
    "Deathly Hallows: Part 1",
    "Deathly Hallows: Part 2",
    "Half-Blood Prince",
    "Prisoner of Azkaban" # You mentioned this in text, though screenshot showed Order of Phoenix. 
                          # This script will look for whatever you list here.
]

# Character Name Mappings (The Logic: Aliases -> Standard Name)
CHARACTER_MAP = {
    # SNAPE
    "SNAPE": "SNAPE",
    "SEVERUS SNAPE": "SNAPE",
    "PROFESSOR SNAPE": "SNAPE",
    "SEVERUS": "SNAPE",
    "YOUNG SEVERUS": "SNAPE",
    
    # RON
    "RON": "RON",
    "RON WEASLEY": "RON",
    
    # HERMIONE
    "HERMIONE": "HERMIONE",
    "HERMIONE GRANGER": "HERMIONE",
    
    # DUMBLEDORE
    "DUMBLEDORE": "DUMBLEDORE",
    "ALBUS DUMBLEDORE": "DUMBLEDORE",
    "PROFESSOR DUMBLEDORE": "DUMBLEDORE",
    "HEADMASTER": "DUMBLEDORE",
    "ALBUS": "DUMBLEDORE"
}

# Regex to find names: Looks for a line that is ALL CAPS (allowing for some punctuation)
# Excludes lines starting with INT. or EXT. (Scene headings)
NAME_PATTERN = re.compile(r"^\s*([A-Z\’\.\-\']+(?:\s+[A-Z\’\.\-\']+)*)(?:\s*\(.*\))?\s*$")
SCENE_HEADING_PATTERN = re.compile(r"^\s*(INT\.|EXT\.|EST\.|I/E\.)")
NOISE_PATTERN = re.compile(r"^\s*(\(CONTINUED\)|CONTINUED:|Rev\.|Blue Revisions|Pink Revisions)")

# ==========================================
# 2. EXTRACTION LOGIC
# ==========================================

def parse_script(filepath, movie_title):
    extracted_data = []
    
    # Counter for Character IDs specific to this movie
    char_counters = {key: 0 for key in set(CHARACTER_MAP.values())}
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    i = 0
    total_lines = len(lines)
    
    while i < total_lines:
        line = lines[i].strip()
        
        # 1. Check if line is a potential Character Name
        name_match = NAME_PATTERN.match(line)
        
        # Logic: Must be all caps, NOT a scene heading, NOT noise
        if (name_match and 
            not SCENE_HEADING_PATTERN.match(line) and 
            not NOISE_PATTERN.search(line)):
            
            raw_name = name_match.group(1).strip()
            
            # 2. Check if this is one of our Target Characters
            if raw_name in CHARACTER_MAP:
                standard_name = CHARACTER_MAP[raw_name]
                
                # Check if there is dialogue following the name
                if i + 1 < total_lines:
                    # Look ahead to grab the dialogue block
                    dialogue_block = []
                    j = i + 1
                    
                    while j < total_lines:
                        d_line = lines[j].strip()
                        
                        # STOP conditions for dialogue:
                        # 1. Empty line (usually separates blocks)
                        # 2. Next line is another All-Caps name or Scene Heading
                        # 3. Next line is Page Number/Noise
                        
                        is_next_name = NAME_PATTERN.match(lines[j]) and not SCENE_HEADING_PATTERN.match(lines[j])
                        is_scene = SCENE_HEADING_PATTERN.match(lines[j])
                        
                        if d_line == "":
                            # If we hit an empty line, usually the speech is over.
                            # However, sometimes page breaks cause gaps.
                            # For safety in raw text, we assume double newline or next cap breaks it.
                            if j + 1 < total_lines and lines[j+1].strip() == "":
                                break
                        elif is_next_name or is_scene:
                            break
                        elif NOISE_PATTERN.search(d_line):
                            j += 1 # Skip noise line
                            continue
                        else:
                            # It is part of the dialogue
                            dialogue_block.append(d_line)
                        
                        j += 1
                    
                    if dialogue_block:
                        # Increment counter for ID
                        char_counters[standard_name] += 1
                        char_id = f"{standard_name}_{char_counters[standard_name]}"
                        
                        full_dialogue = " ".join(dialogue_block)
                        
                        extracted_data.append({
                            "Movie": movie_title,
                            "Character_ID": char_id,
                            "Line_Index": i + 1, # 1-based index
                            "Dialogue": full_dialogue,
                            "Character": standard_name # Helper column
                        })
                    
                    # Move main index forward
                    i = j - 1
        
        i += 1
        
    return extracted_data

# ==========================================
# 3. MAIN EXECUTION
# ==========================================

all_data = []

# Find files in the directory
files_in_dir = os.listdir(INPUT_DIR)

print(f"Scanning {INPUT_DIR}...")

for target in TARGET_MOVIES:
    # Find the matching file for the target movie
    match = next((f for f in files_in_dir if target.lower() in f.lower()), None)
    
    if match:
        print(f"Processing: {match}")
        full_path = os.path.join(INPUT_DIR, match)
        movie_data = parse_script(full_path, target)
        all_data.extend(movie_data)
    else:
        print(f"WARNING: Could not find file for {target}")

# Create DataFrame
df = pd.DataFrame(all_data)

# Save ALL extracted lines
output_filename = "data/all_extracted_dialogue.csv"
df.to_csv(output_filename, index=False)
print(f"\nSuccess! Extracted {len(df)} lines. Saved to {output_filename}")

# ==========================================
# 4. SAMPLING (For your manual assignment)
# ==========================================
# The prompt asks for "For each movie 50... Do it proportionally"
# We will take 50 lines per movie, maintaining the ratio of characters speaking.

sampled_data = []

for movie in df['Movie'].unique():
    movie_df = df[df['Movie'] == movie]
    
    # If the movie has fewer than 50 lines total for these characters, take them all
    n_sample = min(50, len(movie_df))
    
    # Random sample
    sample = movie_df.sample(n=n_sample, random_state=42)
    sampled_data.append(sample)

final_sample = pd.concat(sampled_data)
sample_filename = "data/manual_analysis_sample.csv"
final_sample.to_csv(sample_filename, index=False)

print(f"Created sample dataset for manual analysis: {sample_filename}")
print(final_sample.groupby(['Movie', 'Character']).size())
