import pdf2image
from PyPDF2 import PdfReader
from datetime import datetime

def convert_pdf_to_images(pdf_path):
    """Converts a PDF file to a list of PIL images."""
    return pdf2image.convert_from_path(pdf_path)

def parse_pdf_date(pdf_date):
    """Parses a PDF date format (D:YYYYMMDDHHmmSS) into a readable format."""
    if not pdf_date or not pdf_date.startswith("D:"):
        return "Not available"
    
    try:
        # Extract datetime components
        date_str = pdf_date[2:16]  # Remove "D:" prefix and extract relevant parts
        parsed_date = datetime.strptime(date_str, "%Y%m%d%H%M%S")  # Convert to datetime object
        return parsed_date.strftime("%Y-%m-%d %H:%M:%S")  # Return formatted date
    except ValueError:
        return "Invalid date format"


def get_pdf_metadata(pdf_path):
    """Extracts standard and XMP metadata from a PDF."""
    reader = PdfReader(pdf_path)
    metadata = reader.metadata
    xmp_metadata = metadata.xmp_metadata  # Extract XMP metadata

    return {
        "Pages": len(reader.pages),
        "Title": metadata.get("/Title", "Not available"),
        "Author": metadata.get("/Author", "Not available"),
        "Creator": metadata.get("/Creator", "Not available"),
        "Producer": metadata.get("/Producer", "Not available"),
        "Creation Date": parse_pdf_date(metadata.get("/CreationDate", "Not available")),
        "Modification Date": parse_pdf_date(metadata.get("/ModDate", "Not available")),
        "XMP Metadata": str(xmp_metadata) if xmp_metadata else "No XMP Metadata"
    }