import os
from pathlib import Path
import importlib.util
from pathlib import Path

# Import pdf_to_text from scripts/pdf_to_text.py without requiring package import
spec = importlib.util.spec_from_file_location('pdf_to_text', str(Path(__file__).parent / 'pdf_to_text.py'))
pdf_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pdf_mod)
pdf_to_text = pdf_mod.pdf_to_text

INPUT_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Patterns (case-insensitive substrings) to match the requested PDFs
PATTERNS = [
    'order of the phoenix',
    'chamber of secrets',
    'sorcerer',
]


def find_matching_pdfs():
    matches = []
    for f in INPUT_DIR.iterdir():
        if f.is_file() and f.suffix.lower() == '.pdf':
            name = f.name.lower()
            for p in PATTERNS:
                if p in name:
                    matches.append(f)
                    break
    return matches


if __name__ == '__main__':
    files = find_matching_pdfs()
    if not files:
        print('No matching PDFs found in', INPUT_DIR)
        raise SystemExit(1)

    for pdf in files:
        out_name = pdf.stem + '.txt'
        out_path = OUTPUT_DIR / out_name
        print(f'Converting: {pdf.name} -> {out_path}')
        text = pdf_to_text(pdf)
        with open(out_path, 'w', encoding='utf-8') as fh:
            fh.write(text)
        print(f'Wrote {out_path} ({out_path.stat().st_size} bytes)')
