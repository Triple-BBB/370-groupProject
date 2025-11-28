import pandas as pd
import re

df = pd.read_csv('/mnt/data/final_chars_speeches_cleaned.csv')

proper_names = {"HERMIONE", "RON", "DUMBLEDORE"}

def is_trivial(text):
    words = text.strip().split()
    
    if len(words) >= 3:
        return False

    for w in words:
        cleaned = re.sub(r'[^A-Za-z]', '', w).upper()
        if cleaned in proper_names:
            return False
    
    return True

filtered_df = df[~df['text'].apply(is_trivial)].copy()

out_path = '/mnt/data/final_chars_speeches_cleaned_no_trivial.csv'
filtered_df.to_csv(out_path, index=False)
