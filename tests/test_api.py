
import fitz
import pytest
from fastapi.testclient import TestClient

import app.main as main


client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_document_state(monkeypatch):
    """Keep tests independent of documents uploaded by other tests."""
    monkeypatch.setattr(main, "document_chunks", [])
    monkeypatch.setattr(main, "embedding_model", None)


def make_test_pdf() -> bytes:
    """Create a small PDF in memory for testing."""
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Python is a programming language. "
        "It is often used for data science and artificial intelligence.",
    )
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def test_upload_valid_pdf():
    response = client.post(
        "/upload",
        files={
            "file": (
                "sample.pdf",
                make_test_pdf(),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["pages_with_text"] == 1
    assert data["chunks_created"] >= 1


def test_upload_rejects_non_pdf():
    response = client.post(
        "/upload",
        files={
            "file": (
                "notes.txt",
                b"This is not a PDF.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_ask_rejects_empty_question():
    response = client.post("/ask", json={"question": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty."


def test_ask_requires_uploaded_document():
    response = client.post(
        "/ask",
        json={"question": "What is Python?"},
    )

    assert response.status_code == 400
    assert "Upload a PDF" in response.json()["detail"]



def test_ask_returns_relevant_sources_without_api_key(monkeypatch):
    # Mock the embedding model so no real model is loaded.
    monkeypatch.setattr(
        main,
        "get_embedding_model",
        lambda: object(),
    )

    # Mock embedding generation so the test stays fast.
    monkeypatch.setattr(
        main,
        "build_chunk_embeddings",
        lambda chunks, model: [[0.1, 0.2, 0.3]],
    )

    # Mock search to make the test predictable.
    monkeypatch.setattr(
        main,
        "search_chunks",
        lambda question, chunks, model, top_k, chunk_embeddings=None: [
            {
                "page_number": 1,
                "text": "Python is a programming language.",
                "score": 0.9,
            }
        ],
    )

    monkeypatch.setattr(
        main,
        "document_chunks",
        [
            {
                "page_number": 1,
                "text": "Python is a programming language.",
            }
        ],
    )

    # Ensure the embedding cache starts empty.
    monkeypatch.setattr(main, "document_embeddings", None)
    monkeypatch.setenv("GEMINI_API_KEY", "")

    response = client.post(
        "/ask",
        json={"question": "What is Python?"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["mode"] == "retrieval_only"
    assert len(data["sources"]) == 1
    assert data["sources"][0]["page_number"] == 1
