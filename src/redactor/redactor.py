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
