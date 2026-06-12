"""
Chunker module — splits raw legal text into overlapping word-based chunks
for embedding and vector storage.

Config: 500-word chunks with 100-word overlap.
Chunk ID format: "{topic_id}_chunk_{index}"
"""

import logging

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500       # words per chunk
CHUNK_OVERLAP = 100    # words of overlap between consecutive chunks


def chunk_text(text: str, topic_id: str) -> list[dict]:
    """
    Split text into overlapping chunks.

    Args:
        text: Raw legal text to chunk
        topic_id: Topic identifier (e.g. "pocso") used for chunk IDs

    Returns:
        List of dicts with keys: id, topic_id, content, chunk_index
    """
    words = text.split()

    if not words:
        logger.warning(f"Empty text for topic {topic_id}, returning empty chunks")
        return []

    chunks = []
    start = 0
    index = 0

    while start < len(words):
        end = start + CHUNK_SIZE
        chunk_words = words[start:end]
        chunk_content = " ".join(chunk_words)

        chunk = {
            "id": f"{topic_id}_chunk_{index}",
            "topic_id": topic_id,
            "content": chunk_content,
            "chunk_index": index,
        }
        chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP
        index += 1

    logger.info(
        f"Chunked topic '{topic_id}': {len(words)} words → {len(chunks)} chunks "
        f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})"
    )

    return chunks
