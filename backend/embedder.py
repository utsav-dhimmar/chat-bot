import requests
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_embedding(text: str) -> List[float]:
    """Single text ka embedding nikalo"""
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    return response.json()["embedding"]


def get_embeddings_batch(texts: List[str], max_workers: int = 5) -> List[List[float]]:
    """
    Multiple texts ke embeddings parallel me nikalo
    max_workers = ek saath kitne requests
    """
    embeddings = [None] * len(texts)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(get_embedding, text): i
            for i, text in enumerate(texts)
        }

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            embeddings[index] = future.result()

    return embeddings