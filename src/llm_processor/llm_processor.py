import google.generativeai as genai
import os
from typing import List, Tuple

class LLMProcessor:
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    def generate_cot_reasoning(self, text_span: str, pii_type: str) -> str:
        """Generate chain-of-thought reasoning for PII detection"""
        prompt = f"""
        Analyze the following text and explain why it appears to be a {pii_type}.
        Text: "{text_span}"
        
        Provide a concise explanation in the format:
        "This looks like a {pii_type} because [reasoning]"
        
        Keep the explanation under 100 words.
        """
        
        response = self.model.generate_content(prompt)
        
        return response.text.strip()
