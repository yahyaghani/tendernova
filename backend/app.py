from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from utils.file_processing import convert_pdf_to_images, get_pdf_metadata
from utils.openai_utils import openai_summarize_document
from utils.feature_extraction import extract_features_openai
from utils.data_processing import create_df
from utils.pdf_llbox import get_user_pdf

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the uploads directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_pdf():
    """API to handle PDF upload and process it."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Extract metadata
        metadata = get_pdf_metadata(filepath)

        returned_dict=get_user_pdf(filepath)
        print("Success")
        # # Convert PDF to images
        # images = convert_pdf_to_images(filepath)

        # Analyze document type
    #     # doc_summary = openai_summarize_document(images)
    #     print(type(doc_summary))
    #     print("doc_summary",doc_summary)
    #     if doc_summary.get("BankStatement", False):
    #         extracted_data = extract_features_openai(images)
    #         df = create_df(extracted_data)
    #         return jsonify({"metadata": metadata, "document_type": doc_summary, "extracted_data": df.to_dict()})

    #     return jsonify({"metadata": metadata, "document_type": doc_summary, "message": "Processing skipped for this document type"})

    # return jsonify({"error": "Invalid file format"}), 400

if __name__ == "__main__":
    app.run(debug=True)
