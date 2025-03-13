import re
import hashlib
import json
import os
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# Load the BERT-based NER model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("dslim/bert-large-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-large-NER")
nlp = pipeline("ner", model=model, tokenizer=tokenizer)

# Function to generate a salted hash
def generate_salted_hash(text, salt):
    """Generate a SHA-256 hash with a custom salt."""
    salted_text = salt + text  # Combine salt with original text
    return hashlib.sha256(salted_text.encode()).hexdigest()[:12]  # Take first 12 chars


def save_anonymized_file(anonymized_text, hash_map, output_file, hash_file):
    """
    Saves anonymized text and hash map data to files, preserving the original structure.
    Simply writes the files once without checking for existing content.
    """
    
    # Save the anonymized text file exactly as it is
    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(anonymized_text)

    # Save the hash map to a file
    with open(hash_file, "w", encoding="utf-8") as hash_map_file:
        json.dump(hash_map, hash_map_file, indent=4)

    return output_file, hash_file


# Function to perform NER and regex-based anonymization
def anonymize_text(text, file_path, output_file, hash_file, salt="default_salt", save_to_file=True):
    """
    Anonymizes the text in a given file using BERT-based NER and regex-based detection.
    
    Parameters:
    - text (str): The text file to anonymize.
    - file_path (str): Path to the original file.
    - output_file (str): Path where anonymized text should be saved.
    - hash_file (str): Path where hash mapping should be saved.
    - salt (str): Custom salt for hashing detected entities.
    - save_to_file (bool): Whether to save the anonymized text and hash mapping to files.

    Returns:
    - anonymized_text (str): The text with sensitive entities replaced.
    - hash_map (dict): A dictionary mapping hashes to original values for de-anonymization.
    """
 
    # Perform Named Entity Recognition (NER) on the text
    ner_results = nlp(text)

    # Dictionary to store hashes -> original words
    hash_map = {}

    # Comprehensive regex-based entity detection
    patterns = {
        "email": r"(?:^|\s)[\w!#$%&'*+/=?^`{|}~-](\.?[\w!#$%&'*+/=?^`{|}~-])*@\w+[.-]?\w*\.[a-zA-Z]{2,3}\b",
        "us_phone_number": r"(?:(?:\+?1[-.\s])?\(?\d{3}\)?[-.\s])?\d{3}[-.\s]\d{4}(?:\s(?:x|#|[eE]xt[.]?|[eE]xtension){1} ?\d{1,7})?\b",
        "us_address": r"\d{1,5}(\s[\w\-.,]*){1,6},\s[A-Z]{2}\s\d{5}\b",
        "full_name": r"Full name:\s[A-Z][a-z]+(?:[ \t]*[A-Z]?[a-z]+)?[ \t]*[A-Z][a-z]+\b",
        "us_driver_license": r"\b[A-Za-z]{1}[0-9]{7}\b",
        "us_bank_account": r"Bank Account Number\W*\d{8,17}\b",
        "us_passport": r"(Passport Number|Passport No|Passport #|Passport#|PassportID|Passportno|passportnumber)\W*\d{9}\b",
        "date_generic": r"\b\d{1,4}-\d{1,2}-\d{1,4}\b",
        "consecutive_digits": r"\b\d{6,17}\b"
    }

    custom_ner_results = []
    for pattern_name, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            original_text = match.group().strip()

            # Generate a salted hash
            hash_id = generate_salted_hash(original_text, salt)
            
            # Save mapping for later de-anonymization
            hash_map[hash_id] = original_text  

            # Add to custom NER results
            custom_ner_results.append({
                "word": original_text,
                "start": match.start(),
                "end": match.end(),
                "entity": hash_id,  # Use hash as the entity tag
                "score": 1.0
            })

    # Combine Transformer-based NER and Custom NER detections
    all_ner_results = sorted(ner_results + custom_ner_results, key=lambda e: e["start"])

    # Function to replace detected entities
    def replace_entities(text, entities):
        """Replaces named entities in text with their respective tags while maintaining structure."""
        offset = 0  # Track cumulative position shifts
        modified_text = text  # Working copy

        for entity in sorted(entities, key=lambda e: e["start"]):  
            start, end = entity["start"] + offset, entity["end"] + offset
            entity_tag = f"[{entity['entity']}]"  # Either BERT NER tag or hashed ID

            # Replace entity with its tag
            modified_text = modified_text[:start] + entity_tag + modified_text[end:]

            # Adjust offset based on length change
            offset += len(entity_tag) - (end - start)

        return modified_text

    # Apply entity replacement while preserving all whitespace and formatting
    anonymized_text = replace_entities(text, all_ner_results)

    # Save results to files if requested
    if save_to_file:
        save_anonymized_file(anonymized_text, hash_map, output_file, hash_file)
        
    return anonymized_text, hash_map, output_file, hash_file

# # Usage example (commented out)
# file_name = "original_text.txt"
# with open(file_name, "r", encoding="utf-8") as file:
#     content = file.read()
# anonymized_text, hash_map, saved_anonymized_file, saved_hash_file = anonymize_text(
#     content, 
#     file_name, 
#     "anonymized_output.txt", 
#     "hash_mapping.json", 
#     save_to_file=True
# )