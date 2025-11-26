import pdfplumber
from pathlib import Path


def pdf_to_text(pdf_path):
    """Extract full text from a pdf file and return as a single string.

    Args:
        pdf_path (str or Path): Path to the PDF file.

    Returns:
        str: Extracted text (may be empty if pdfplumber cannot read pages).
    """
    pdf_path = Path(pdf_path)
    text = ""
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_text.py <pdf-path>")
        sys.exit(1)
    pdf = sys.argv[1]
    out = pdf_to_text(pdf)
    print(out[:1000])

