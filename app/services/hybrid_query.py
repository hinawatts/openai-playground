from __future__ import annotations
from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select
from qdrant_client.models import Filter, FieldCondition, MatchAny
from ..models import Student
from ..vector.qdrant_client import get_qdrant_client
from .embedding_service import embed_text
import os

_COLLECTION = os.getenv("QDRANT_COLLECTION", "student_notes")


def sql_candidates_by_absences(db: Session, min_absences: int) -> List[int]:
    stmt = select(Student.id).where(Student.absences > min_absences)
    return [row[0] for row in db.execute(stmt).all()]


def vector_search_notes_for_students(query: str, student_ids: List[int], top_k: int = 10) -> List[Dict[str, Any]]:
    if not student_ids:
        return []
    client = get_qdrant_client()
    query_vec = embed_text(query)
    flt = Filter(must=[FieldCondition(key="student_id", match=MatchAny(any=student_ids))
                       ])

    hits = client.search(collection_name=_COLLECTION, query_vector=query_vec, limit=top_k, query_filter=flt,
                         with_payload=True,
                         )
    # Normalize result shape
    return [
        {
            "note_id": h.id,
            "score": float(h.score),
            "student_id": h.payload.get("student_id"),
            "text": h.payload.get("text"),
        }
        for h in hits
    ]


def hybrid_query(db: Session, semantic_query: str, min_absences: int = 5, top_k: int = 10) -> Dict[str, Any]:


    candidates = sql_candidates_by_absences(db, min_absences)
    hits = vector_search_notes_for_students(semantic_query, candidates, top_k=top_k)

# Group hits by student_id
    by_student: Dict[int, List[Dict[str, Any]]] = {}
    for h in hits:
       sid = int(h["student_id"]) if h.get("student_id") is not None else None
       if sid is None:
           continue
       by_student.setdefault(sid, []).append(h)

# Fetch student rows for matched ids
    matched_ids = list(by_student.keys())
    if not matched_ids:
        return {
            "sql_applied": {"min_absences": min_absences, "candidates": len(candidates)},
            "vector_query": {"q": semantic_query, "top_k": top_k},
            "students": [],
        }

    rows = db.execute(select(Student).where(Student.id.in_(matched_ids))).scalars().all()


    students = [
    {
        "student_id": s.id,
        "full_name": s.full_name,
        "absences": s.absences,
        "notes_matches": sorted(by_student[s.id], key=lambda x: -x["score"]),
    }
    for s in rows
]


    return {
    "sql_applied": {"min_absences": min_absences, "candidates": len(candidates)},
    "vector_query": {"q": semantic_query, "top_k": top_k},
    "students": students,
    }
