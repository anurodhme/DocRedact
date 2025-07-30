# DocRedact-Lite Implementation Guide

## Project Overview
Build a private data redaction tool that uses chain-of-thought reasoning with LLMs to identify and explain PII redactions in documents.

## Step-by-Step Implementation

### 1. Project Setup and Dependencies

#### Initialize Project Structure
```bash
mkdir docredact-lite
cd docredact-lite
mkdir -p src/{parsers,pii_detector,llm_processor,redactor,ui}
touch requirements.txt README.md .gitignore
```

#### Install Dependencies
```bash
# requirements.txt
pip install python-dotenv streamlit PyPDF2 pandas openpyxl spacy transformers torch requests
```

#### Download spaCy Models
```bash
python -m spacy download en_core_web_sm
```

### 2. Document Parsing Module

#### Create PDF Parser (`src/parsers/pdf_parser.py`)
```python
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
```

#### Create Excel Parser (`src/parsers/excel_parser.py`)
```python
import pandas as pd
from typing import str

def extract_text_from_excel(excel_path: str) -> str:
    """Extract text from Excel file"""
    df = pd.read_excel(excel_path)
    return df.to_string()
```

### 3. PII Detection Module

#### Create PII Detector (`src/pii_detector/pii_detector.py`)
```python
import spacy
import re
from typing import List, Tuple

class PIIDetector:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{16}\b'
        }
    
    def detect_pii(self, text: str) -> List[Tuple[str, str, int, int]]:
        """Detect PII entities in text"""
        pii_entities = []
        
        # spaCy NER detection
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["PERSON", "ORG", "GPE"]:
                pii_entities.append((ent.text, ent.label_.lower(), ent.start_char, ent.end_char))
        
        # Regex pattern matching
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                pii_entities.append((match.group(), pii_type, match.start(), match.end()))
        
        return pii_entities
```

### 4. LLM Processing Module

#### Create LLM Processor (`src/llm_processor/llm_processor.py`)
```python
import openai
import os
from typing import List, Tuple

class LLMProcessor:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def generate_cot_reasoning(self, text_span: str, pii_type: str) -> str:
        """Generate chain-of-thought reasoning for PII detection"""
        prompt = f"""
        Analyze the following text and explain why it appears to be a {pii_type}.
        Text: "{text_span}"
        
        Provide a concise explanation in the format:
        "This looks like a {pii_type} because [reasoning]"
        
        Keep the explanation under 100 words.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )
        
        return response.choices[0].message.content.strip()
```

### 5. Redaction Module

#### Create Redactor (`src/redactor/redactor.py`)
```python
import re
from typing import List, Tuple

def redact_text(text: str, pii_entities: List[Tuple[str, str, int, int]]) -> Tuple[str, List[dict]]:
    """Redact PII from text and return redacted text with explanations"""
    # Sort entities by position (reverse order to maintain indices)
    sorted_entities = sorted(pii_entities, key=lambda x: x[2], reverse=True)
    
    redacted_text = text
    redaction_report = []
    
    for entity_text, entity_type, start, end in sorted_entities:
        # Redact the entity
        redacted_text = redacted_text[:start] + "[REDACTED]" + redacted_text[end:]
        
        # Add to report
        redaction_report.append({
            "original_text": entity_text,
            "type": entity_type,
            "position": (start, end)
        })
    
    return redacted_text, redaction_report
```

### 6. Streamlit UI Application

#### Create Main App (`src/ui/app.py`)
```python
import streamlit as st
import os
from src.parsers.pdf_parser import extract_text_from_pdf
from src.parsers.excel_parser import extract_text_from_excel
from src.pii_detector.pii_detector import PIIDetector
from src.llm_processor.llm_processor import LLMProcessor
from src.redactor.redactor import redact_text

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

st.title("DocRedact-Lite")
st.write("Upload documents to automatically redact private information")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF or Excel file", type=["pdf", "xlsx"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    with open(f"temp_{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Extract text based on file type
    if uploaded_file.name.endswith('.pdf'):
        text = extract_text_from_pdf(f"temp_{uploaded_file.name}")
    else:
        text = extract_text_from_excel(f"temp_{uploaded_file.name}")
    
    st.subheader("Original Text")
    st.text_area("Document Content", text, height=200)
    
    # PII Detection
    detector = PIIDetector()
    pii_entities = detector.detect_pii(text)
    
    if pii_entities:
        st.subheader("Detected PII Entities")
        for entity in pii_entities:
            st.write(f"- {entity[0]} ({entity[1]})")
        
        # LLM Reasoning
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            llm_processor = LLMProcessor(api_key)
            reasoning_results = []
            
            for entity_text, entity_type, _, _ in pii_entities:
                reasoning = llm_processor.generate_cot_reasoning(entity_text, entity_type)
                reasoning_results.append({
                    "text": entity_text,
                    "type": entity_type,
                    "reasoning": reasoning
                })
            
            # Redact text
            redacted_text, redaction_report = redact_text(text, pii_entities)
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Redacted Text")
                st.text_area("Redacted Content", redacted_text, height=200)
            
            with col2:
                st.subheader("Redaction Explanations")
                for result in reasoning_results:
                    st.write(f"**{result['text']}** ({result['type']})")
                    st.write(result['reasoning'])
                    st.write("---")
        else:
            st.error("OpenAI API key not found. Please set OPENAI_API_KEY in environment variables.")
    else:
        st.info("No PII entities detected in the document.")
    
    # Clean up temporary file
    os.remove(f"temp_{uploaded_file.name}")
```

### 7. GitHub Actions Workflow

#### Create CI/CD Workflow (`.github/workflows/redact-docs.yml`)
```yaml
name: Redact Documents

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'

jobs:
  redact-documents:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        python -m spacy download en_core_web_sm
    
    - name: Redact documents
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        # Add redaction script here
    
    - name: Commit and push redacted files
      run: |
        git config --global user.name 'github-actions[bot]'
        git config --global user.email 'github-actions[bot]@users.noreply.github.com'
        git checkout -b redacted
        # Add redacted files
        git add redacted/
        git commit -m "Auto-redact documents"
        git push origin redacted --force
```

### 8. Environment Configuration

#### Create `.env` file
```env
OPENAI_API_KEY=your_openai_api_key_here
```

#### Update `.gitignore`
```gitignore
.env
temp_*
__pycache__/
*.pyc
```

### 9. Benchmarking with Presidio (Extra Credit)

#### Install Presidio
```bash
pip install presidio-analyzer presidio-anonymizer
```

#### Create Benchmark Script (`src/benchmark/benchmark.py`)
```python
from presidio_analyzer import AnalyzerEngine
from src.pii_detector.pii_detector import PIIDetector

def benchmark_recall(text: str):
    """Compare recall between custom detector and Presidio"""
    # Custom detector
    custom_detector = PIIDetector()
    custom_entities = custom_detector.detect_pii(text)
    
    # Presidio detector
    analyzer = AnalyzerEngine()
    presidio_results = analyzer.analyze(text=text, language='en')
    
    # Calculate recall metrics
    # Implementation details...
```

### 10. Testing and Validation

#### Create Test Script (`tests/test_pipeline.py`)
```python
import unittest
from src.pii_detector.pi_detector import PIIDetector

class TestPIIDetection(unittest.TestCase):
    def test_email_detection(self):
        detector = PIIDetector()
        text = "Contact me at john.doe@example.com"
        entities = detector.detect_pii(text)
        self.assertTrue(any(entity[1] == 'email' for entity in entities))

if __name__ == '__main__':
    unittest.main()
```

### 11. Deployment Instructions

1. **Local Development**:
   ```bash
   streamlit run src/ui/app.py
   ```

2. **Environment Setup**:
   - Set `OPENAI_API_KEY` environment variable
   - Install all dependencies from `requirements.txt`

3. **GitHub Actions**:
   - Add `OPENAI_API_KEY` as repository secret
   - Configure workflow to trigger on docs folder changes

### 12. Future Enhancements

- Add support for more file types (Word, images)
- Implement custom redaction patterns
- Add user interface for reviewing and approving redactions
- Integrate with cloud storage services
- Add batch processing capabilities

## Project Completion Checklist

- [ ] Document parsing functionality implemented
- [ ] PII detection with spaCy and regex working
- [ ] LLM integration for chain-of-thought reasoning
- [ ] Redaction and explanation report generation
- [ ] Streamlit UI for user interaction
- [ ] GitHub Actions workflow configured
- [ ] Benchmarking against Presidio implemented
- [ ] Comprehensive testing completed
- [ ] Documentation and README updated