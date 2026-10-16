
import fitz

from app.pdf_processor import extract_pages


def test_extract_pages_preserves_page_numbers():
    document = fitz.open()

    page1 = document.new_page()
    page1.insert_text((72, 72), "Dijkstra's algorithm")

    page2 = document.new_page()
    page2.insert_text((72, 72), "Shortest path problem")

    pdf_bytes = document.tobytes()
    document.close()

    pages = extract_pages(pdf_bytes)

    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert "Dijkstra's algorithm" in pages[0]["text"]
    assert pages[1]["page_number"] == 2
    assert "Shortest path problem" in pages[1]["text"]
