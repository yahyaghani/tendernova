import pdf2image
from PyPDF2 import PdfReader

def convert_pdf_to_images(pdf_path):
    """Converts a PDF file to a list of PIL images."""
    return pdf2image.convert_from_path(pdf_path)

def get_pdf_metadata(pdf_path):
    """Extracts metadata from a PDF."""
    reader = PdfReader(pdf_path)
    metadata = reader.metadata
    return {
        "Pages": len(reader.pages),
        "Title": metadata.get("/Title", "Not available"),
        "Author": metadata.get("/Author", "Not available"),
        "Creator": metadata.get("/Creator", "Not available"),
        "Producer": metadata.get("/Producer", "Not available"),
        "Creation Date": metadata.get("/CreationDate", "Not available"),
        "Modification Date": metadata.get("/ModDate", "Not available"),
    }
