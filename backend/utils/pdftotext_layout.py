import subprocess
import json
import spacy
import hashlib
import os 

# from utils.privacy_ner_bert import anonymize_text
# Paths


def extract_text_with_pdftotext(pdf_path,extract_text_file_path):
    """Extract text from a PDF while retaining layout using pdftotext"""
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    # extracted_text_with_layout = f"basetext_{base_filename}.txt"

    try:
        subprocess.run(["pdftotext", "-layout", pdf_path, extract_text_file_path], check=True)
    except FileNotFoundError:
        print("❌ Error: `pdftotext` is not installed. Install `poppler-utils` on Linux or `pdftotext.exe` on Windows.")
        exit(1)
    
    # Read the extracted structured text
    with open(extract_text_file_path, "r", encoding="utf-8") as f:
        extracted_text = f.read()
    
    return extracted_text,extract_text_file_path

def extract_tables_with_pdfplumber(pdf_path):
    """Extract tables from a PDF and save them as a CSV using pdfplumber"""
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    extracted_csv = f"{base_filename}.csv"

    try:
        # Run pdfplumber as a subprocess
        subprocess.run(["pdfplumber", "<", pdf_path, ">", extracted_csv], shell=True, check=True)
    except FileNotFoundError:
        print("❌ Error: `pdfplumber` is not installed. Install it using `pip install pdfplumber`.")
        exit(1)
    
    return extracted_csv

