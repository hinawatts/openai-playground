import os
from typing import cast, Optional, List

from openai import OpenAI
from qdrant_client import models
from openai.types.chat import ChatCompletionMessageParam

from app.services.embedding_service import embed_texts
from app.vector.qdrant_client import get_qdrant_client

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_student(student):
    content = f"""
    Student: {student.full_name} 
    Absences: {student.absences},
    Notes: {student.notes or "No additional notes"}
"""
    messages = cast(list[ChatCompletionMessageParam], [
        {"role": "system", "content": "You are an assistant summarizing student performance."},
        {"role": "user", "content": f"Summarize this student:\n{content}"}
    ])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content


def summarize_student_with_question(question: str, context):
    messages = cast(list[ChatCompletionMessageParam], [
        {"role": "system", "content": "You are an assistant summarizing student performance."},
        {"role": "user", "content": f"Question:{question}\n\nNotes: \n" + "\n".join(context)}
    ])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content


def summarize_student_from_chunked_data(question: str, top_k: int, student_id: Optional[str] = None,
                                        doc_id: Optional[str] = None):
    qvec = embed_texts(question)[0]
    filters = []
    if doc_id:
        filters.append(models.FieldCondition(key="doc_id", match=models.MatchValue(value=doc_id)))
    if student_id:
        filters.append(models.FieldCondition(key="student_id", match=models.MatchValue(value=student_id)))
    flt = models.Filter(must=filters) if filters else None
    hits = get_qdrant_client().search(collection_name=os.getenv("QDRANT_COLLECTION_CHUNKS"), query_filter=flt,
                                      query_vector=qvec, limit=top_k, with_payload=True)
    contexts, sources = [], []
    for h in hits:
        chunk = h.payload.get("text","")
        idx = h.payload.get("chunk_index","?")
        contexts.append(f"[chunk {idx}] {chunk}")
        sources.append({
            "doc_id": h.payload.get("doc_id"),
            "chunk_id": h.id,
            "chunk_index": idx,
            "score": h.score,
            "preview": (chunk[:200] + "…") if len(chunk) > 200 else chunk,
            "source_name": h.payload.get("source_name")
        })
    if not contexts:
        return None
    answer = generate_answer(question, contexts)
    return answer, sources


def generate_answer(question: str, contexts: List[str]) -> str:
    system = (
        "You are a helpful assistant for summarizing and answering questions "
        "based strictly on the provided context. If unknown, say you don't know."
    )
    user = (
        f"Question:\n{question}\n\n"
        "Context (cite like [chunk N]):\n" + "\n\n".join(contexts) +
        "\n\nAnswer succinctly and include inline citations like [chunk N] where relevant."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=cast(list[ChatCompletionMessageParam],[
            {"role":"system","content":system},
            {"role":"user","content":user}
        ]),
        temperature=0.2,
    )
    return resp.choices[0].message.content
