"""
Example demonstrating how to chunk a document in Langbase.
"""
import os
from langbase import Langbase

# Get API key from environment variable or provide directly
api_key = os.environ.get("LANGBASE_API_KEY", "your-api-key")

# Initialize the client
lb = Langbase(api_key=api_key)

# Path to document to chunk
document_path = "path/to/your/document.txt"  # Change this to your document path
document_name = "article.txt"

# Chunk the document
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

    # Read the file content
    with open(document_path, "rb") as file:
        document_content = file.read()

    # Chunk the document
    chunks = lb.chunk(
        document=document_content,
        document_name=document_name,
        content_type=content_type,
        chunk_max_length="1000",  # Optional: maximum chunk length
        chunk_overlap="100",      # Optional: overlap between chunks
        separator="\n\n"          # Optional: custom separator
    )

    print(f"Successfully chunked document into {len(chunks)} chunks")
    print()

    # Display chunks
    for i, chunk in enumerate(chunks, 1):
        print(f"Chunk {i} ({len(chunk)} characters):")
        # Print a preview if the chunk is long
        preview = (chunk[:200] + "...") if len(chunk) > 200 else chunk
        print(preview)
        print("-" * 80)

except Exception as e:
    print(f"Error chunking document: {e}")
