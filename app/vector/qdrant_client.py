from __future__ import annotations
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


def get_qdrant_client() -> QdrantClient:
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    return QdrantClient(url=url, api_key=api_key, timeout=20)
    # return QdrantClient(host=host, port=port)


def ensure_collection(client: QdrantClient, collection: str, vector_size: int = 1536) -> None:
    from qdrant_client.http.exceptions import UnexpectedResponse
    try:
        info = client.get_collection(collection)
        # If exists but with different params, you might recreate – keep it simple for now
        _ = info
    except UnexpectedResponse:
        client.create_collection(collection_name=collection, vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
)
