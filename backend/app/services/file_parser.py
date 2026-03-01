"""
services/file_parser.py
-----------------------
Extract text from uploaded files. Adapted from Dev 1's file_parser.py.

Changes from Dev 1's version:
  - Added DOCX, TXT, CSV, MD support (was PDF only)
  - Replaced PyPDF2 with pymupdf (better text extraction, handles scanned PDFs)
  - Returns same format Dev 1 used: List[Dict] with page_number + content
    so chunker.py works without changes

Supports: PDF, DOCX, TXT, CSV, MD
"""

from pathlib import Path
from typing import Dict, List


def extract_pages(file_path: str) -> List[Dict]:
    """
    Extract text from any supported file.
    Returns: [{"page_number": 1, "content": "text..."}, ...]

    For non-PDF files, the entire content is treated as page 1.
    This matches Dev 1's chunker.py expected input format.
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext == ".docx":
        return _extract_docx(file_path)
    elif ext in (".txt", ".md"):
        return _extract_text_file(file_path)
    elif ext == ".csv":
        return _extract_csv(file_path)
    else:
        raise ValueError(
            f"Unsupported file type: '{ext}'\nAllowed: .pdf .docx .txt .md .csv"
        )


def get_page_count(file_path: str) -> int:
    """Return number of pages (PDF) or 1 for other file types."""
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        try:
            import fitz

            doc = fitz.open(file_path)
            count = len(doc)
            doc.close()
            return count
        except Exception:
            return 1
    return 1


def _extract_pdf(file_path: str) -> List[Dict]:
    """Extract PDF using pymupdf — better than PyPDF2 for complex layouts."""
    try:
        import fitz  # pymupdf
    except ImportError:
        raise ImportError("pymupdf not installed. Run: uv add pymupdf")

    doc = fitz.open(file_path)
    pages = []

    for page_num in range(len(doc)):
        text = doc[page_num].get_text().strip()
        if text:
            pages.append(
                {
                    "page_number": page_num + 1,
                    "content": text,
                }
            )

    doc.close()

    if not pages:
        raise ValueError(
            "No text found in PDF. "
            "The file may be scanned/image-only or password protected."
        )

    return pages


def _extract_docx(file_path: str) -> List[Dict]:
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx not installed. Run: uv add python-docx")

    doc = Document(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    if not paragraphs:
        raise ValueError("No text found in DOCX file.")

    return [{"page_number": 1, "content": "\n\n".join(paragraphs)}]


def _extract_text_file(file_path: str) -> List[Dict]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()

    if not content:
        raise ValueError("File is empty.")

    return [{"page_number": 1, "content": content}]


def _extract_csv(file_path: str) -> List[Dict]:
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas not installed. Run: uv add pandas")

    df = pd.read_csv(file_path)
    content = df.to_string(index=False)

    if not content.strip():
        raise ValueError("CSV file is empty.")

    return [{"page_number": 1, "content": content}]
