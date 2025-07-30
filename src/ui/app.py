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
        api_key = os.getenv("GEMINI_API_KEY")
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
            st.error("Gemini API key not found. Please set GEMINI_API_KEY in environment variables.")
    else:
        st.info("No PII entities detected in the document.")
    
    # Clean up temporary file
    os.remove(f"temp_{uploaded_file.name}")
