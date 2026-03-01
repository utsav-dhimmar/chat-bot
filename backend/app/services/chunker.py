"""
services/chunker.py
-------------------
Dev 1's chunker.py — kept exactly as-is, just moved to correct location.

Takes List[Dict] pages from file_parser.extract_pages()
Returns List[Dict] chunks with chunk_index, page_number, content
"""

from typing import Dict, List


def chunk_text(
    pages: List[Dict], chunk_size: int = 500, overlap: int = 50
) -> List[Dict]:
    """
    Pages ko chunks me todo.

    chunk_size = characters per chunk
    overlap    = character overlap between chunks (for context continuity)

    Returns: [{"chunk_index": 0, "page_number": 1, "content": "text..."}, ...]
    """
    chunks = []
    chunk_index = 0

    for page in pages:
        text = page["content"]
        page_number = page["page_number"]

        # Short page — add as single chunk
        if len(text) <= chunk_size:
            chunks.append(
                {
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                    "content": text,
                }
            )
            chunk_index += 1
            continue

        # Long page — split into overlapping chunks
        start = 0
        while start < len(text):
            end = start + chunk_size

            # Don't cut mid-word — find nearest space
            if end < len(text):
                while end > start and text[end] != " ":
                    end -= 1

            chunk_content = text[start:end].strip()

            if chunk_content:
                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "page_number": page_number,
                        "content": chunk_content,
                    }
                )
                chunk_index += 1

            start = end - overlap  # step back by overlap

    return chunks
