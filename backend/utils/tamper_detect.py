import pandas as pd
import numpy as np
import os
import subprocess
import json
from sklearn.ensemble import IsolationForest

def detect_pdf_tampering(pdf_file_path):
    """
    Detects potential tampering in a PDF file by extracting its structure and analyzing anomalies.
    
    Parameters:
        pdf_file_path (str): Path to the PDF file.
        
    Returns:
        str: JSON object containing suspected tampered elements.
    """
    try:
        # Step 1: Generate CSV filename based on PDF name
        csv_file_path = pdf_file_path.replace(".pdf", "_.csv")

        # Step 2: Run pdfplumber command to extract data into CSV
        command = f"pdfplumber < {pdf_file_path} > {csv_file_path}"
        subprocess.run(command, shell=True, check=True)

        # Step 3: Load the generated CSV file
        df = pd.read_csv(csv_file_path)

        # Define all possible features for anomaly detection
        possible_features = ['x0', 'x1', 'y0', 'y1', 'width', 'height', 'linewidth']

        # Select only the features that exist in the dataset
        features = [col for col in possible_features if col in df.columns]

        if not features:
            return json.dumps({"error": "No valid numeric features found in the dataset."})

        # Drop rows with missing values in selected features
        df = df.dropna(subset=features)

        # Step 4: Train Isolation Forest model
        iso_forest = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
        df['anomaly_score'] = iso_forest.fit_predict(df[features])

        # Isolation Forest returns:
        # -1 (anomalous/tampered)
        #  1 (normal)
        df['tampered'] = df['anomaly_score'] == -1

        # Step 5: Filter tampered rows
        tampered_df = df[df['tampered']]

        if tampered_df.empty:
            return json.dumps({"message": "No tampering detected."})

        # Convert tampered elements to JSON
        tampered_json = tampered_df[['page_number'] + features + ['anomaly_score', 'tampered']].to_dict(orient="records")

        return json.dumps({"tampered_elements": tampered_json}, indent=4)

    except subprocess.CalledProcessError as e:
        return json.dumps({"error": f"pdfplumber command failed: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

# Example usage
pdf_file = "halifax.pdf"
tampering_results = detect_pdf_tampering(pdf_file)
print(tampering_results)  # JSON output
