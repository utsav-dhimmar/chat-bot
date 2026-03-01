import PyPDF2
from typing import List, Dict


def extract_text_from_pdf(file_path: str) -> List[Dict]:
    """
    PDF se text extract karo - page by page
    Returns: [{"page_number": 1, "content": "text..."}, ...]
    """
    pages = []

    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        total_pages = len(reader.pages)

        for page_num in range(total_pages):
            page = reader.pages[page_num]
            text = page.extract_text()

            # Empty pages skip karo
            if text and text.strip():
                pages.append({"page_number": page_num + 1, "content": text.strip()})

    return pages


def get_page_count(file_path: str) -> int:
    """PDF me kitne pages hain"""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return len(reader.pages)
