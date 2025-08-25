import os

from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import FieldCondition, MatchValue, Filter
from qdrant_client.models import Distance, VectorParams, PointStruct

load_dotenv()
# Load clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

COLLECTION = "student_notes"
VECTOR_SIZE = 1536  # matches OpenAI text-embedding-3-small

# 1. Ensure collection exists
try:
    qdrant.get_collection(COLLECTION)
except:
    qdrant.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )

# 2. Helper to embed text
def embed_text(text: str):
    return openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    ).data[0].embedding

# 3. Insert some notes
notes = [
    (1, "Alice is strong in math and problem-solving.", ["math", "problem-solving"]),
    (2, "Bob struggles with essay writing and grammar.",["writing", "grammar"]),
    (3, "Cathy is quiet in class but shows strong interest in physics.",["physics"]),
    (4, "David often misses lectures but is very active in group projects.",["attendance"])
]

for note_id, text, tags in notes:
    qdrant.upsert(
        collection_name=COLLECTION,
        points=[
            PointStruct(
                id=note_id,
                vector=embed_text(text),
                payload={"note_id": note_id, "text": text, "tags": tags}
            )
        ]
    )

print("Inserted sample notes ✅")

# 4. Query
query = "Who struggles with writing?"
query_vec = embed_text(query)

filter = Filter(
    must=[
        FieldCondition(
            key="tags",
            match=MatchValue(value="writing")
        )
    ])
results = qdrant.search(
    collection_name=COLLECTION,
    query_vector=query_vec,
    query_filter=filter,
    limit=3,
    with_payload=True
)

print(f"\nQuery: {query}")
for r in results:
    print(f"Score: {r.score:.3f} | Note: {r.payload['text']}")