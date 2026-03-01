"""
services/dspy_module.py
-----------------------
Anti-hallucination RAG brain using HuggingFace Inference Providers.

WHY THIS APPROACH:
  The old approach (dspy.LM("huggingface/...")) broke because HF's free
  serverless tier no longer hosts large LLMs directly. As of mid-2025,
  HuggingFace routes LLM requests through Inference Providers (SambaNova,
  Together AI, etc.) via their router at https://router.huggingface.co

  This version uses HuggingFace's InferenceClient directly, which handles
  provider routing automatically with just your HF_TOKEN — still free.

HOW IT WORKS:
  InferenceClient(api_key=HF_TOKEN) -> router.huggingface.co -> picks fastest
  free provider automatically -> returns answer.

RECOMMENDED FREE MODELS (confirmed working via HF router):
  - Qwen/Qwen2.5-7B-Instruct              <- RECOMMENDED, great for RAG
  - meta-llama/Llama-3.2-3B-Instruct      <- fast, small, good quality
  - HuggingFaceTB/SmolLM3-3B             <- lightest, very fast on free tier
  - microsoft/Phi-3-mini-4k-instruct      <- good quality, small size

SET IN .env:
  LLM_PROVIDER=huggingface
  LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
  HF_TOKEN=hf_your_token_here
"""

import os
from typing import Optional

# ── Config helper ──────────────────────────────────────────────────────────


def _cfg(key: str, default: str = "") -> str:
    """Read from pydantic settings if available, else from env vars."""
    try:
        from app.core.config import settings

        return str(getattr(settings, key, default))
    except (ImportError, AttributeError):
        return os.getenv(key, default)


# ── Anti-hallucination system prompt ───────────────────────────────────────

SYSTEM_PROMPT = """You are a precise document assistant.

Your ONLY job is to answer the user's question using the context excerpts provided.
These excerpts come directly from a file the user uploaded.

STRICT RULES - follow all of these without exception:
1. Answer ONLY using information present in the provided context.
2. Do NOT use any outside knowledge, training data, or general facts.
3. Do NOT guess, infer beyond what is stated, or make up information.
4. If the answer is not clearly present in the context, respond with EXACTLY:
   "I could not find an answer in your uploaded documents."
5. Keep your answer concise and directly relevant to the question.
6. You may quote short phrases from the context to support your answer."""

FALLBACK_MESSAGE = "I could not find an answer in your uploaded documents."

_VAGUE_PHRASES = [
    "i don't know",
    "i cannot answer",
    "not enough information",
    "the context does not",
    "no information provided",
    "cannot be determined",
    "not mentioned in",
    "not provided in",
    "i'm not sure",
    "i am not sure",
]


# ── Simple result object ────────────────────────────────────────────────────


class Prediction:
    """Mimics dspy.Prediction so rag_engine.py needs no changes."""

    def __init__(self, answer: str):
        self.answer = answer


# ── Main RAG module ─────────────────────────────────────────────────────────


class RAGModule:
    """
    Anti-hallucination RAG module using HuggingFace InferenceClient.

    Uses the HF router (router.huggingface.co) which automatically picks
    the fastest free inference provider for the chosen model.
    """

    def __init__(self, model: str, hf_token: str):
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            raise ImportError(
                "huggingface_hub is not installed.\nRun:  uv add huggingface-hub"
            )

        self.model = model
        self.client = InferenceClient(api_key=hf_token)
        print(f"[RAG] InferenceClient ready - model: {model}")

    def __call__(self, context: str, question: str) -> Prediction:
        """
        Run anti-hallucination Q&A.
        Returns Prediction with .answer attribute.
        """
        user_message = (
            "Here are the relevant excerpts from the uploaded document:\n\n"
            "--- CONTEXT START ---\n"
            f"{context}\n"
            "--- CONTEXT END ---\n\n"
            f"Based ONLY on the context above, answer this question:\n{question}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=512,
                temperature=0.01,
                top_p=0.9,
            )
            answer = response.choices[0].message.content.strip()

        except Exception as e:
            err = str(e)

            if any(
                x in err for x in ["not supported", "not available", "404", "not found"]
            ):
                raise RuntimeError(
                    f"\nModel '{self.model}' is not available on the free HF Inference API.\n\n"
                    "Change LLM_MODEL in your .env to one of these confirmed working models:\n"
                    "  LLM_MODEL=Qwen/Qwen2.5-7B-Instruct          <- RECOMMENDED\n"
                    "  LLM_MODEL=meta-llama/Llama-3.2-3B-Instruct\n"
                    "  LLM_MODEL=HuggingFaceTB/SmolLM3-3B          <- lightest, fastest\n"
                    "  LLM_MODEL=microsoft/Phi-3-mini-4k-instruct\n"
                )
            if "401" in err or "unauthorized" in err.lower():
                raise RuntimeError(
                    "\nHF_TOKEN is invalid or expired.\n"
                    "Go to https://huggingface.co/settings/tokens\n"
                    "Delete old token -> New token -> Read scope -> paste in .env"
                )
            if "429" in err or "rate limit" in err.lower():
                raise RuntimeError(
                    "\nRate limit hit (free tier: ~30 req/min). Wait 60 sec and retry."
                )
            if "503" in err or "loading" in err.lower():
                raise RuntimeError(
                    "\nModel is cold-starting on HF servers. Wait 20-30 sec and retry."
                )
            raise RuntimeError(f"\nHuggingFace API error: {err}")

        # Guard: empty response
        if not answer or len(answer) < 5:
            answer = FALLBACK_MESSAGE

        # Guard: model expresses uncertainty
        elif any(phrase in answer.lower() for phrase in _VAGUE_PHRASES):
            answer = FALLBACK_MESSAGE

        return Prediction(answer=answer)


# ── OpenAI fallback adapter ─────────────────────────────────────────────────


class _OpenAIAdapter:
    """Used only when LLM_PROVIDER=openai in .env"""

    def __init__(self):
        import dspy

        class _GroundedQA(dspy.Signature):
            __doc__ = SYSTEM_PROMPT
            context: str = dspy.InputField(desc="Document excerpts")
            question: str = dspy.InputField(desc="User question")
            answer: str = dspy.OutputField(desc="Answer from context only")

        self._gen = dspy.ChainOfThought(_GroundedQA)

    def __call__(self, context: str, question: str) -> Prediction:
        pred = self._gen(context=context, question=question)
        answer = (pred.answer or FALLBACK_MESSAGE).strip()
        if any(p in answer.lower() for p in _VAGUE_PHRASES):
            answer = FALLBACK_MESSAGE
        return Prediction(answer=answer)


# ── Singleton management ────────────────────────────────────────────────────

_rag_module: Optional[RAGModule] = None


def init_dspy() -> None:
    """
    Build the RAGModule singleton based on .env config.
    Call once at app startup in main.py @app.on_event("startup").
    """
    global _rag_module

    provider = _cfg("LLM_PROVIDER", "huggingface").lower()

    if provider == "huggingface":
        hf_token = _cfg("HF_TOKEN", "")
        model = _cfg("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")

        if not hf_token or not hf_token.startswith("hf_"):
            raise ValueError(
                "\nHF_TOKEN is missing or invalid in your .env file.\n"
                "Steps:\n"
                "  1. Go to https://huggingface.co/settings/tokens\n"
                "  2. New token -> Read scope -> Generate\n"
                "  3. Paste into .env:  HF_TOKEN=hf_xxxxxxxxxxxx"
            )

        _rag_module = RAGModule(model=model, hf_token=hf_token)
        print(f"[DSPy] Ready - provider=huggingface, model={model}")

    elif provider == "openai":
        import dspy

        api_key = _cfg("OPENAI_API_KEY", "")
        model = _cfg("LLM_MODEL", "gpt-4o-mini")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")
        lm = dspy.LM(
            model=f"openai/{model}",
            api_key=api_key,
            max_tokens=512,
            temperature=0.0,
        )
        dspy.configure(lm=lm)
        _rag_module = _OpenAIAdapter()
        print(f"[DSPy] Ready - provider=openai, model={model}")

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider}'. Use 'huggingface' or 'openai'."
        )


def get_rag_module() -> RAGModule:
    """Return singleton RAGModule. Initialises on first call."""
    global _rag_module
    if _rag_module is None:
        init_dspy()
    return _rag_module
