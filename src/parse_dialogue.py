from pathlib import Path
import re

# configurations
MOVIE_FILE = Path("data/processed/harry-potter-and-the-sorcerers-stone-2001.txt")
OUTPUT_ALL = Path("data/processed/sorcerers_stone_speeches.tsv")
OUTPUT_FOUR = Path("data/processed/sorcerers_stone_four_chars.tsv")
CHARACTERS_OF_INTEREST = {"RON", "HERMIONE", "VOLDEMORT", "SNAPE", "VOLDEMONT"}
FIRST_SECOND_PRONOUNS = {"i", "im", "ive", "id", "we", "were", "you", "youre", "youll", "youve", "us", "my", "our"}
THIRD_PRONOUNS = {"he", "she", "they", "him", "her", "them", "his", "hers", "their", "theirs"}
SCENE_HEADER_RE = re.compile(r'^\d+\s+(INT\.|EXT\.)\b')



def is_character_cue(line: str) -> bool:
    # a character cue line is mostly uppercase letters/spaces, short-ish, and not clearly a header or comment.
    line = line.strip()

    if not line:
        return False

    #ignore non-character uppercase stuff
    bad_starts = ("INT.", "CONTINUED", "CUT TO", "DISSOLVE TO", "FADE OUT", "FADE IN")
    if line.startswith(bad_starts):
        return False

    #must contain at least one letter
    if not any(c.isalpha() for c in line):
        return False

    #if contains any digit we reject
    if any(ch.isdigit() for ch in line):
        return False

    #allow only letters space and dots
    if not re.fullmatch(r"[A-Z .]+", line):
        return False
    
    #if its not all uppercase
    if line.upper() != line:
        return False
    
    #reject if there is any punctuation that doesnt belong in names
    bad_punctation = {",", "?", "!", ":", ";","..."}
    if any (p in line for p in bad_punctation):
        return False

    #too long probably not a name
    if len(line)>30:
        return False

    if len(line.split()) > 4:
        return False
    
    return True

def build_canonical_names(lines):
    # form all lines, collect character cues and simple title case variant for use in action line
    names = set()
    for raw in lines:
        line = raw.strip()
        if is_character_cue(line):
            names.add(line) # full cue NARCISSA MALFOY
            first = line.split()[0]
            names.add(first.title()) #Narcissa
            names.add(first.upper())#NARCISSA
    return names

# if there is pronouns or indications that this is spoken at the first or second person likely not stage directions
def has_first_or_second_person(line:str) -> bool:
    words = re.findall(r"[A-Za-z']+", line.lower())
    return any(w in FIRST_SECOND_PRONOUNS for w in words)

#if there are third pronouns without first or second pronouns probably indicate that this is stage instructions
def has_third_person_only(line:str) -> bool:
    words = re.findall(r"[A-Za-z']+", line.lower())
    if not words:
        return False
    has_third = any(w in THIRD_PRONOUNS for w in words)
    has_first_second = any(w in FIRST_SECOND_PRONOUNS for w in words)
    return has_third and not has_first_second

def looks_like_new_cue(line: str) -> bool:
    # we reuse character cue logic for non-current speakers
    return is_character_cue(line)

def is_action_line(line: str, current_speaker: str, canonical_names: set) -> bool:

    line = line.strip()
    if not line:
        return False
    
    #if there is int or ext in the line
    if "INT." in line or "EXT." in line:
        return True
    #scene headers and contined markers
    if SCENE_HEADER_RE.match(line):
        return True
    if line.startswith(("INT.", "EXT.")):
        return True
    if "CONTINUED" in line and any(ch.isdigit()for ch in line):
        return True

    #stage directions in parentheses
    if line.startswith("("):
        return True
    
    tokens = line.split()
    if not tokens:
        return False
    
    first = tokens[0]
    first_upper = first.upper()

    # if the line starts with the current speaker name and the second word is lowercase probably a verb
    if current_speaker is not None and line.startswith(current_speaker):
        tokens = line.split()
        if len(tokens) >=2:
            second = tokens[1]
            if second and second[0].islower():
                return True
    
    #if there is a name other than speaker and there is no comma after it probably stage directions
    if (first in canonical_names or first_upper in canonical_names) and (current_speaker is None or first_upper != current_speaker):
        if len(tokens) >=2:
            second = tokens[1]
            if second != ",":
                #example bill doesnt smile, or bellatrix walks away ...
                return True
    #long narratives, mentions a character but no I/you 
    if len(tokens) >15 and not has_first_or_second_person(line):
        if any(name in line for name in canonical_names):
            return True
    # third person narrative, third person pronouns without any first or second pronouns, so no I YOU US, OUR ...
    if has_third_person_only(line):
        return True

    #if it has I/You bias toward speech
    if has_first_or_second_person(line):
        return False
    
    #default we treat as speech we might cleanup later
    return False


def parse_script(path: Path):
    #parse a single script text file into speech acts
    # each speech act is one character + merged dialogue lines.

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = [l.strip("\n") for l in text.splitlines()]

    canonical_names = build_canonical_names(lines)

    speeches = []
    current_speaker = None
    current_buffer = []
    speech_id = 0
    in_action_block = False

    for raw_line in lines:
        line = raw_line.strip()

        #New character cue line
        if is_character_cue(line):
            in_action_block = False #leaving action mode
            #flush previous speech(merging all lines in one
            if current_speaker and current_buffer:
                speech_id +=1
                speeches.append({
                    "character": current_speaker,
                    "speech_id": speech_id,
                    "text": " ".join(current_buffer).strip()
                })
                current_buffer = []

            current_speaker = line # eg "HERMIONE", "RON", "VOLDEMORT"
            continue 
        
        # if we dont have a speaker yet, ignore
        if current_speaker is None:
            continue 
        
        #if we in an action block we skip until the next cue
        if in_action_block:
            continue

        #end of speech if action line
        if is_action_line(line,current_speaker, canonical_names):
            if current_buffer:
                speech_id += 1
                speeches.append({
                    "character": current_speaker,
                    "speech_id": speech_id,
                    "text": " ".join(current_buffer).strip()
                })
                current_buffer = []
            in_action_block = True
            continue
  
        #otherwise we treat as dialogue: append to current buffer
        current_buffer.append(line)

    # we flush the last speech
    if current_speaker and current_buffer:
        speech_id +=1
        speeches.append({
            "character": current_speaker,
            "speech_id": speech_id,
            "text": " ".join(current_buffer).strip()
        })
    
    return speeches

def write_tsv(path: Path, rows):
    with path.open("w", encoding="utf-8") as f:
        f.write("character\tspeech_id\ttext\n")
        for r in rows:
            text = r["text"].replace("\t", " ").replace("\n", " ")
            f.write(f"{r['character']}\t{r['speech_id']}\t{text}\n")


def main():
    print(f"Parsing: {MOVIE_FILE}")
    speeches = parse_script(MOVIE_FILE)
    print(f"Total speech acts found: {len(speeches)}")

    # Save ALL speeches (all characters)
    write_tsv(OUTPUT_ALL, speeches)
    print(f"Saved ALL speeches → {OUTPUT_ALL}")

    # Show which character names we actually found (for debugging)
    unique_chars = sorted({s["character"] for s in speeches})
    print("Characters detected:")
    for name in unique_chars:
        print("  ", name)

    # Filter to your 4 characters of interest
    filtered = [s for s in speeches if s["character"] in CHARACTERS_OF_INTEREST]
    print(f"Speech acts for target characters ({CHARACTERS_OF_INTEREST}): {len(filtered)}")

    write_tsv(OUTPUT_FOUR, filtered)
    print(f"Saved target characters' speeches → {OUTPUT_FOUR}")


if __name__ == "__main__":
    main()

