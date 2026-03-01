from typing import Dict, List


def chunk_text(
    pages: List[Dict], chunk_size: int = 500, overlap: int = 50
) -> List[Dict]:
    """
    Pages ko chunks me todо

    chunk_size = ek chunk me kitne characters
    overlap = chunks ke beech overlap (context ke liye)

    Returns: [{"chunk_index": 0, "page_number": 1, "content": "text..."}, ...]
    """
    chunks = []
    chunk_index = 0

    for page in pages:
        text = page["content"]
        page_number = page["page_number"]

        # Agar text chunk_size se chota hai toh seedha add karo
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

        # Bada text toh chunks me todo
        start = 0
        while start < len(text):
            end = start + chunk_size

            # Word ke beech mat todo - pura word lo
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

            # Overlap ke saath aage badho
            start = end - overlap

    return chunks
