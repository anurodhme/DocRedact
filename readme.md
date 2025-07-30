# DocRedact-Lite

## Project Overview
Build a private data redaction tool that uses chain-of-thought reasoning with LLMs to identify and explain PII redactions in documents.

## Features
- Detect PII entities (emails, phone numbers, credit cards, names, organizations, locations) in documents
- Redact identified PII entities
- Provide explanations for why entities were flagged using Google's Gemini API
- Support for PDF and Excel documents
- Web-based UI using Streamlit

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download spaCy model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
4. Set up environment variables in `.env` file (GEMINI_API_KEY)

## Usage

Run the Streamlit app:
```bash
streamlit run src/ui/app.py
```

## Dependencies
- Python 3.7+
- Streamlit
- PyPDF2
- pandas
- openpyxl
- spaCy
- transformers
- torch
- google-generativeai

## Future Enhancements
- Add support for more file types (Word, images)
- Implement custom redaction patterns
- Add user interface for reviewing and approving redactions
- Integrate with cloud storage services
- Add batch processing capabilities
