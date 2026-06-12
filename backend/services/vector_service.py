"""
Vector service — ChromaDB storage and retrieval using local embeddings.

- Embedding model: sentence-transformers/all-MiniLM-L6-v2
- ChromaDB: PersistentClient at CHROMA_DB_PATH
- Collection name = topic_id (e.g. "pocso", "rti")
"""

import os
import logging
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_chroma_client: chromadb.PersistentClient | None = None
_embedding_model: SentenceTransformer | None = None


def get_chroma_client() -> chromadb.PersistentClient:
    """Get or create the ChromaDB PersistentClient singleton."""
    global _chroma_client
    if _chroma_client is None:
        logger.info(f"Initializing ChromaDB PersistentClient at: {CHROMA_DB_PATH}")
        _chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _chroma_client


def get_embedding_model() -> SentenceTransformer:
    """Get or create the SentenceTransformer embedding model singleton."""
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def _get_or_create_collection(topic_id: str) -> chromadb.Collection:
    """Get or create a ChromaDB collection for a topic."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=topic_id,
        metadata={"hnsw:space": "cosine"},
    )


def store_chunks(topic_id: str, chunks: list[dict]) -> int:
    """
    Embed and store text chunks in ChromaDB.

    Args:
        topic_id: Topic identifier (used as collection name)
        chunks: List of dicts with keys: id, content, chunk_index

    Returns:
        Number of chunks stored
    """
    if not chunks:
        logger.warning(f"No chunks to store for topic: {topic_id}")
        return 0

    collection = _get_or_create_collection(topic_id)
    model = get_embedding_model()

    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [
        {"topic_id": chunk["topic_id"], "chunk_index": chunk["chunk_index"]}
        for chunk in chunks
    ]

    embeddings = model.encode(documents, show_progress_bar=False).tolist()

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    logger.info(f"Stored {len(chunks)} chunks in collection '{topic_id}'")
    return len(chunks)


def retrieve_chunks(topic_id: str, query: str, top_k: int = 5) -> list[dict]:
    """
    Retrieve the most relevant chunks for a query from a topic collection.

    Args:
        topic_id: Topic identifier (collection name)
        query: User's question text
        top_k: Number of top results to return

    Returns:
        List of dicts with keys: id, content, score, chunk_index
    """
    collection = _get_or_create_collection(topic_id)
    model = get_embedding_model()

    if collection.count() == 0:
        logger.warning(f"Collection '{topic_id}' is empty, no results to return")
        return []

    query_embedding = model.encode([query], show_progress_bar=False).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []
    for i in range(len(results["ids"][0])):
        retrieved.append({
            "id": results["ids"][0][i],
            "content": results["documents"][0][i],
            "score": 1 - results["distances"][0][i],  
            "chunk_index": results["metadatas"][0][i].get("chunk_index", 0),
        })

    logger.info(
        f"Retrieved {len(retrieved)} chunks for query in '{topic_id}' "
        f"(top score: {retrieved[0]['score']:.3f})" if retrieved else
        f"No chunks retrieved for query in '{topic_id}'"
    )

    return retrieved


def delete_collection(topic_id: str) -> None:
    """Delete a topic's ChromaDB collection (used during re-ingestion)."""
    client = get_chroma_client()
    try:
        client.delete_collection(name=topic_id)
        logger.info(f"Deleted collection: {topic_id}")
    except ValueError:
        logger.info(f"Collection '{topic_id}' does not exist, nothing to delete")
