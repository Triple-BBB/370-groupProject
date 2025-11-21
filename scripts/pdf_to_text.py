import pdfplumber
from pathlib import path

def pdf_to_text(pdf_path):
    #Extract full text from a pdf file
    text =""
    with pdfplumber.open(pdf_path) as pdf:
        for pages in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text +"\n"
    return text

