from __future__ import annotations
import os
from typing import Iterable
from openai import OpenAI


_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

def embed_texts(texts: Iterable[str]) -> list[list[float]]:
   """Return embeddings for a list of texts (ordered)."""
   texts = [t if t is not None else "" for t in texts]
   resp = _client.embeddings.create(model=_MODEL, input=list(texts))
   return [d.embedding for d in resp.data]

def embed_text(text: str) -> list[float]:
   return embed_texts([text])[0]