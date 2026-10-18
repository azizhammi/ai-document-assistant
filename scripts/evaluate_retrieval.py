
import json
import sys
from pathlib import Path

# Add the project root to Python's import path.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sentence_transformers import SentenceTransformer
from app.search import search_chunks

DATASET_PATH = ROOT / "evaluation" / "benchmark.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 3


def load_dataset():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_question(question, chunks, model, top_k=TOP_K):
    relevant_ids = set(question["relevant_chunk_ids"])

    results = search_chunks(
        question=question["question"],
        chunks=chunks,
        model=model,
        top_k=top_k,
    )

    retrieved_ids = [chunk["id"] for chunk in results]
    hits = set(retrieved_ids) & relevant_ids

    recall = len(hits) / len(relevant_ids)
    precision = len(hits) / len(retrieved_ids) if retrieved_ids else 0.0

    reciprocal_rank = 0.0
    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant_ids:
            reciprocal_rank = 1.0 / rank
            break

    return {
        "recall": recall,
        "precision": precision,
        "reciprocal_rank": reciprocal_rank,
        "retrieved_ids": retrieved_ids,
    }


def main():
    dataset = load_dataset()
    chunks = dataset["chunks"]
    questions = dataset["questions"]

    model = SentenceTransformer(MODEL_NAME)

    results = []

    for question in questions:
        metrics = evaluate_question(question, chunks, model)

        results.append(metrics)

        print(f"\nQuestion: {question['question']}")
        print(f"Retrieved: {metrics['retrieved_ids']}")
        print(f"Recall@{TOP_K}: {metrics['recall']:.3f}")
        print(f"Precision@{TOP_K}: {metrics['precision']:.3f}")
        print(f"Reciprocal rank: {metrics['reciprocal_rank']:.3f}")

    count = len(results)

    if count == 0:
        raise ValueError("The benchmark contains no questions.")

    mean_recall = sum(r["recall"] for r in results) / count
    mean_precision = sum(r["precision"] for r in results) / count
    mrr = sum(r["reciprocal_rank"] for r in results) / count

    print("\n" + "=" * 40)
    print(f"Questions evaluated: {count}")
    print(f"Mean Recall@{TOP_K}: {mean_recall:.3f}")
    print(f"Mean Precision@{TOP_K}: {mean_precision:.3f}")
    print(f"MRR@{TOP_K}: {mrr:.3f}")


if __name__ == "__main__":
    main()
