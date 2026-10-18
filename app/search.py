
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[dict]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    chunks = []

    for page in pages:
        text = page["text"].strip()
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "page_number": page["page_number"],
                    "text": chunk_text,
                })

            if end == len(text):
                break

            start = end - overlap

    return chunks

def build_chunk_embeddings(
    chunks: list[dict],
    model: SentenceTransformer,
):
    """Embed document chunks once so their vectors can be reused."""
    if not chunks:
        return None

    return model.encode(
        [chunk["text"] for chunk in chunks],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    
    

def search_chunks(
    question: str,
    chunks: list[dict],
    model: SentenceTransformer,
    top_k: int = 3,
    chunk_embeddings=None,
) -> list[dict]:
    if not question.strip():
        raise ValueError("Question must not be empty")

    if top_k <= 0:
        raise ValueError("top_k must be positive")

    if not chunks:
        return []

    # Reuse cached document vectors when provided.
    if chunk_embeddings is None:
        chunk_embeddings = build_chunk_embeddings(chunks, model)

    question_embedding = model.encode(
        [question],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )[0]

    scores = chunk_embeddings @ question_embedding

    ranked_indices = sorted(
        range(len(chunks)),
        key=lambda index: float(scores[index]),
        reverse=True,
    )[:top_k]

    return [
        {**chunks[index], "score": float(scores[index])}
        for index in ranked_indices
    ]

