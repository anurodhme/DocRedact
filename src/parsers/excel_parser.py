import pandas as pd
from typing import str

def extract_text_from_excel(excel_path: str) -> str:
    """Extract text from Excel file"""
    df = pd.read_excel(excel_path)
    return df.to_string()
