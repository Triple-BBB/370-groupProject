import pdfplumber
from pathlib import Path

# Paths are RELATIVE TO THE PROJECT ROOT
RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")

def pdf_to_text(pdf_path):
    """Extract full text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def main():
    print(f"RAW_DIR  = {RAW_DIR.resolve()}")
    print(f"OUT_DIR  = {OUT_DIR.resolve()}")

    OUT_DIR.mkdir(exist_ok=True)

    pdf_files = list(RAW_DIR.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF(s) in data/raw")

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        text = pdf_to_text(pdf_file)
        out_path = OUT_DIR / f"{pdf_file.stem}.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"Saved -> {out_path}")

    print("done")

if __name__ == "__main__":
    main()
