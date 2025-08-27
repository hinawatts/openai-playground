import os
import re
import uuid
from typing import List, Optional
import datetime as dt
import tiktoken
from qdrant_client import QdrantClient, models

from app.services.embedding_service import embed_texts
from app.vector.qdrant_client import get_qdrant_client, ensure_collection

_COLLECTION = os.getenv("QDRANT_COLLECTION_CHUNKS", "student_notes")
_enc = tiktoken.get_encoding("cl100k_base")

def upload_file(text: str, max_tokens: int, overlap_tokens: int, source_name: str, student_id: Optional[str]) -> str:
    chunks = upload(text, max_tokens, overlap_tokens)
    return upsert_chunks(chunks, source_name, student_id)

def upload(text, max_tokens, overlap_tokens)-> List[str]:
    client = get_qdrant_client()
    ensure_collection(client, _COLLECTION, vector_size=1536)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks: List[str] = []
    buf: List[str] = []
    cur = 0
    def flush():
        nonlocal buf, cur
        if not buf:
            return
        combined = " ".join(buf).strip()
        chunks.append(combined)
        if overlap_tokens > 0:
            ids = _enc.encode(combined)
            tail = _enc.decode(ids[max(0, len(ids) - overlap_tokens):])
            buf = [tail]
            cur = count_tokens(tail)
        else:
            buf = []
            cur = 0

    for s in sentences:
        st = count_tokens(s)
        if cur + st > max_tokens and buf:
            flush()
        buf.append(s)
        cur += st

    if buf:
        chunks.append(" ".join(buf).strip())

    return [c for c in chunks if c.strip()]

def count_tokens(text: str) -> int:
    return len(_enc.encode(text))

def upsert_chunks(chunks: List[str],source_name: str, student_id: Optional[str] = None) -> str:
    client = get_qdrant_client()
    ensure_collection(client, _COLLECTION, vector_size=1536)
    doc_id = str(uuid.uuid4())
    now =  dt.datetime.now()
    points = []
    vectors = embed_texts(chunks)
    for i, (text, vec) in enumerate(zip(chunks,vectors)):
        points.append(
            models.PointStruct(
                id = str(uuid.uuid4()),
                vector = vec,
                payload={
                    "doc_id": doc_id,
                    "student_id": student_id,
                    "chunk_index": i,
                    "text": text,
                    "source_name": source_name,
                    "created_at": now,
                    "type": "feedback_text",
                },
            )
        )
    get_qdrant_client().upsert(collection_name=_COLLECTION, points=points)
    return doc_id