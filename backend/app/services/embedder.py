"""
services/embedder.py
--------------------
Async wrappers around Dev 1's Ollama embedding functions.

Dev 1's original:  sync, uses requests + ThreadPoolExecutor
This version:      async-compatible for FastAPI event loop

Kept Dev 1's batch logic (parallel requests via ThreadPoolExecutor)
but wrapped in asyncio.run_in_executor so FastAPI doesn't freeze.

REQUIREMENT: Ollama must be running with nomic-embed-text pulled.
  ollama pull nomic-embed-text
  ollama serve
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import requests

from app.core.config import settings

OLLAMA_URL = settings.OLLAMA_BASE_URL


# ── Dev 1's original sync functions (kept intact) ─────────────────────────────


def get_embedding(text: str) -> List[float]:
    """Single text ka embedding nikalo (sync — Dev 1's original)"""
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": settings.EMBEDDING_MODEL, "prompt": text},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["embedding"]


def get_embeddings_batch(texts: List[str], max_workers: int = 5) -> List[List[float]]:
    """
    Multiple texts ke embeddings parallel me nikalo (sync — Dev 1's original).
    max_workers = ek saath kitne requests
    """
    embeddings = [None] * len(texts)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(get_embedding, text): i for i, text in enumerate(texts)
        }
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            embeddings[index] = future.result()

    return embeddings


# ── Async wrappers for FastAPI (your additions) ────────────────────────────────


async def embed_query(text: str) -> List[float]:
    """
    Async wrapper around get_embedding.
    Used in: services/rag_engine.py and api/documents.py
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_embedding, text)


async def embed_batch(texts: List[str]) -> List[List[float]]:
    """
    Async wrapper around get_embeddings_batch.
    Used in: api/documents.py during upload processing.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_embeddings_batch, texts)
