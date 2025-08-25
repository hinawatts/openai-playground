from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PayloadSchemaType
import os
load_dotenv()
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

qdrant.create_payload_index(
    collection_name="student_notes",
    field_name="tags",
    field_schema=PayloadSchemaType.KEYWORD
)

print("Index for tags created ✅")