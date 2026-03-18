import os
import json
import chromadb
from chromadb.utils import embedding_functions

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(PROJECT_ROOT, "chroma_storage")
CHUNKS_FILE = os.path.join(PROJECT_ROOT, "vector_db", "processed_chunks.json")


def embed_documents():
    if not os.path.exists(CHUNKS_FILE):
        print(f"❌ processed_chunks.json not found at {CHUNKS_FILE}")
        return

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not chunks:
        print("❌ No chunks to embed.")
        return

    print(f"🗄️  Connecting to ChromaDB at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Use chromadb's built-in sentence-transformers embedding function
    # This avoids direct sentence_transformers import version issues
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Delete and recreate for clean state
    try:
        client.delete_collection("company_documents")
    except Exception:
        pass

    collection = client.create_collection(
        name="company_documents",
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )

    print(f"🔢 Embedding {len(chunks)} chunks...")
    batch_size = 32
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [c["text"] for c in batch]

        metas = []
        for c in batch:
            m = dict(c["metadata"])
            if isinstance(m.get("allowed_roles"), list):
                m["allowed_roles"] = ", ".join(m["allowed_roles"])
            # Remove non-primitive values
            m = {k: v for k, v in m.items() if isinstance(v, (str, int, float, bool))}
            metas.append(m)

        collection.add(
            ids=[c["id"] for c in batch],
            documents=texts,
            metadatas=metas
        )
        print(f"  Embedded {min(i+batch_size, len(chunks))}/{len(chunks)} chunks")

    print(f"✅ Done — {collection.count()} chunks stored in ChromaDB.")


if __name__ == "__main__":
    embed_documents()
