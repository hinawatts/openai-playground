from __future__ import annotations
import os
from typing import Optional
from qdrant_client.models import PointStruct
from .embedding_service import embed_text
from ..vector.qdrant_client import get_qdrant_client, ensure_collection


_COLLECTION = os.getenv("QDRANT_COLLECTION", "student_notes")

def upsert_student_note(student_id: int, note_id: int, text: str) -> None:
   client = get_qdrant_client()
   ensure_collection(client, _COLLECTION, vector_size=1536)
   vector = embed_text(text)
   point = PointStruct(id=note_id, vector=vector,payload={"student_id": student_id,"text": text,},
)
   client.upsert(collection_name=_COLLECTION, points=[point])

def delete_student_note(note_id: int) -> None:
  client = get_qdrant_client()
  client.delete(collection_name=_COLLECTION, points_selector={"points": [note_id]})

def get_notes(top_k: int, question: str):
    client = get_qdrant_client()
    query_vec = embed_text(question)
    hits = client.search(collection_name=_COLLECTION, query_vector=query_vec, limit=top_k, with_payload=True)
    return [
         {
              "note_id": h.id,
              "score": float(h.score),
              "student_id": h.payload.get("student_id"),
              "text": h.payload.get("text"),
         }
         for h in hits
    ]