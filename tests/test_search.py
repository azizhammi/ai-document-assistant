
import pytest

from app.search import chunk_pages


def test_chunk_pages_preserves_page_numbers():
    pages = [
        {
            "page_number": 2,
            "text": "A" * 1000,
        }
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=400,
        overlap=50,
    )

    assert len(chunks) == 3
    assert all(chunk["page_number"] == 2 for chunk in chunks)
    assert len(chunks[0]["text"]) == 400
    assert chunks[0]["text"][-50:] == chunks[1]["text"][:50]


def test_empty_pages_produce_no_chunks():
    assert chunk_pages([]) == []


def test_invalid_overlap_is_rejected():
    with pytest.raises(ValueError):
        chunk_pages(
            [{"page_number": 1, "text": "Example"}],
            chunk_size=100,
            overlap=100,
        )
