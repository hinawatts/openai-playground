# Student Management API with AI Search  

This project is a **FastAPI-based CRUD application** for managing students, extended with **semantic search powered by Qdrant and OpenAI embeddings**.  

It combines a traditional relational database (**Postgres + SQLAlchemy**) with a vector database (**Qdrant**) to enable both structured queries (SQL) and semantic queries (AI embeddings).  

---

## Features  

- **CRUD operations** on students (create, read, update, delete).  
- Stores students in **Postgres** with fields:  
  - `full_name`  
  - `email`  
  - `is_active`  
  - `absences`  
  - `notes`  
- **Semantic search on notes**:  
  - Notes embedded via **OpenAI embeddings**.  
  - Vectors stored in **Qdrant**.  
  - Queries return students by *meaning* (not just keywords).  
- **Hybrid filtering**: Combine SQL filters (`min_absences`) with vector search.  
- **AI-powered endpoint**: AI generated summary for a student based on the notes.  
- **RAG endpoint**: Introduced a Retrieval-Augmented Generation flow.  
  - Retrieves top-K relevant notes from Qdrant.  
  - Uses GPT (`gpt-4o-mini`) to generate natural-language summaries or answers.
- **AI summaries**: Questions like *“Which students are struggling with writing?”* return a concise AI-generated answer instead of just raw notes.  
- **Document Chunking for RAG**:
  - Supports uploading long text documents (e.g., feedback reports).
  - Chunks documents into smaller pieces for embedding and storage in Qdrant.
  - Enables semantic search and RAG on large documents.
  - Improves answer precision by focusing on relevant sections.
  - Reduces token usage and costs by avoiding feeding entire documents to the LLM.

## 🛠️ Tech Stack  

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)  
- **Database (structured)**: Postgres + SQLAlchemy ORM  
- **Database (vector)**: [Qdrant](https://qdrant.tech/)  
- **Embeddings**: OpenAI `text-embedding-3-small` (1536 dimensions)  
- **Environment**: Docker Compose, Python 3.12  
- **Dependencies**: see `requirements.txt`  

---
