#!/usr/bin/env python3
"""
Main entry point for the document redaction tool.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pii_detector.pii_detector import PIIDetector
from src.redactor.redactor import redact_text


def redact_file(input_path, output_path):
    """Redact a single file and save to output path."""
    detector = PIIDetector()
    
    # Read the input file
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Detect PII entities
    pii_entities = detector.detect_pii(content)
    
    # Redact the content
    redacted_content, redaction_report = redact_text(content, pii_entities)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Write redacted content to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(redacted_content)
    
    print(f"Redacted {input_path} -> {output_path}")
    print(f"Redacted {len(redaction_report)} PII entities")
    
    return redaction_report


def redact_directory(input_dir, output_dir):
    """Redact all files in a directory and save to output directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory {input_dir} does not exist")
    
    total_redacted = 0
    
    # Process all files in the input directory
    for file_path in input_path.rglob('*'):
        if file_path.is_file():
            # Calculate relative path
            relative_path = file_path.relative_to(input_path)
            output_file = output_path / relative_path
            
            try:
                redact_file(str(file_path), str(output_file))
                total_redacted += 1
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    print(f"\nRedaction complete. Processed {total_redacted} files.")


def main():
    parser = argparse.ArgumentParser(description='Redact PII from documents')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('output', help='Output file or directory')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        redact_file(str(input_path), args.output)
    elif input_path.is_dir():
        redact_directory(str(input_path), args.output)
    else:
        print(f"Error: {args.input} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
