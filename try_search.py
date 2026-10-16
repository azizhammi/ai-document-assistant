
from app.search import chunk_pages, search_chunks

pages = [
    {
        "page_number": 1,
        "text": (
            "Dijkstra's algorithm finds shortest paths "
            "from a source vertex in a graph with "
            "non-negative edge weights."
        ),
    },
    {
        "page_number": 2,
        "text": (
            "Binary search finds a target in a sorted "
            "array by repeatedly dividing the search "
            "interval in half."
        ),
    },
    {
        "page_number": 3,
        "text": (
            "Breadth-first search explores a graph "
            "level by level and can find shortest paths "
            "in unweighted graphs."
        ),
    },
]

chunks = chunk_pages(pages)

print("Loading the embedding model...")
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

question = "Which algorithm finds the shortest route in a graph?"

results = search_chunks(question, chunks, model, top_k=2)

for result in results:
    print(f"\nPage: {result['page_number']}")
    print(f"Score: {result['score']:.3f}")
    print(f"Text: {result['text']}")
