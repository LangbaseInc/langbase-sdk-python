"""
Example demonstrating how to upload a document to a memory in Langbase.
"""
import os
from langbase import Langbase

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

# Memory name where to upload the document
memory_name = "product-knowledge"

# Path to the document to upload
document_path = "path/to/your/document.pdf"  # Change this to your document path
document_name = "product-manual.pdf"  # Name to assign to the document

# Metadata for the document
document_metadata = {
    "product": "Widget Pro 2000",
    "version": "v2.1",
    "department": "Engineering",
    "language": "English"
}

# Upload the document
try:
    # Ensure file exists
    if not os.path.exists(document_path):
        raise FileNotFoundError(f"Document not found at {document_path}")

    # Determine content type based on file extension
    file_extension = os.path.splitext(document_path)[1].lower()
    content_type_map = {
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel"
    }

    content_type = content_type_map.get(file_extension)
    if not content_type:
        raise ValueError(f"Unsupported file type: {file_extension}")

    # Upload the document
    upload_response = lb.memories.documents.upload(
        memory_name=memory_name,
        document_name=document_name,
        document=document_path,
        content_type=content_type,
        meta=document_metadata
    )

    print(f"Successfully uploaded document '{document_name}' to memory '{memory_name}'")
    print(f"Status code: {upload_response.status_code}")

except Exception as e:
    print(f"Error uploading document: {e}")
