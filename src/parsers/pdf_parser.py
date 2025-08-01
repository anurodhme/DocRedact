import PyPDF2
from typing import List

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text
