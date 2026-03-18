import os
import chromadb
from chromadb.utils import embedding_functions

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(PROJECT_ROOT, "chroma_storage")

_client = None
_collection = None
_ef = None


def get_ef():
    global _ef
    if _ef is None:
        _ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    return _ef


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name="company_documents",
            embedding_function=get_ef(),
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def is_authorized(user_role: str, allowed_roles_raw) -> bool:
    if user_role == "C-Level":
        return True
    if isinstance(allowed_roles_raw, list):
        roles = allowed_roles_raw
    else:
        roles = [r.strip() for r in str(allowed_roles_raw).split(",")]
    return user_role in roles


def secure_semantic_search(query: str, user_role: str, top_k: int = 3) -> list:
    collection = get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(top_k * 3, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    authorized = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, dists):
        allowed = meta.get("allowed_roles", "")
        if is_authorized(user_role, allowed):
            authorized.append({
                "document": doc,
                "metadata": meta,
                "similarity_score": round(1 - dist, 4)
            })
        if len(authorized) >= top_k:
            break

    return authorized
