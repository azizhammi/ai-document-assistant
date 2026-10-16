# DocuMind — AI Document Assistant

DocuMind is a web application that lets users upload a PDF and ask questions about its contents. It searches the document for relevant passages and uses them to answer questions, with page references to help users check the information themselves.

I built this project to get hands-on experience with Python, backend development, semantic search, and integrating a language model into a working application.

## Features

- **PDF processing:** Extracts text from PDF documents while preserving page numbers.
- **Semantic search:** Finds relevant passages based on the meaning of a question, rather than relying only on exact keyword matches.
- **Question answering:** Uses the OpenAI API to generate answers based on retrieved document passages.
- **Source references:** Displays relevant passages and their page numbers so users can verify the answers.
- **Retrieval-only mode:** Still retrieves relevant passages when an OpenAI API key is not configured.
- **Web interface:** Provides PDF upload, chat, suggested questions, document statistics, and chat reset functionality.
- **Automated tests:** Covers PDF processing, search behavior, API endpoints, and document handling.

## Tech stack

- **Python** — application logic
- **FastAPI** — backend and REST API
- **Streamlit** — user interface
- **PyMuPDF** — PDF text extraction
- **Sentence Transformers** — text embeddings
- **NumPy** — similarity calculations
- **OpenAI API** — answer generation
- **Pytest** — automated testing

## How it works

1. The user uploads a PDF.
2. The backend extracts its text and splits it into smaller, overlapping chunks.
3. Sentence Transformers converts the question and document chunks into embeddings.
4. The application ranks passages by cosine similarity and selects the most relevant ones.
5. If an OpenAI API key is configured, the selected passages are sent to the language model to generate an answer.
6. The interface displays the answer and the retrieved passages, including their page numbers.

Without an API key, the application returns the most relevant passages instead of generating an answer.

## Getting started

### Requirements

- Python 3.11 or newer
- Git
- An OpenAI API key for generated answers (optional)

### 1. Clone the repository

```bash
git clone https://github.com/azizhammi/ai-document-assistant.git
cd ai-document-assistant
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the environment's Python directly using `.venv\Scripts\python.exe`.

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the OpenAI API (optional)

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini
```

Replace the placeholder with your own API key. API usage may incur charges. Never commit your `.env` file or share your API key.

Without these settings, the application can still retrieve relevant passages from uploaded documents.

### 5. Start the backend

In the first terminal, run:

```bash
python -m uvicorn app.main:app --reload
```

The API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 6. Start the frontend

Open a second terminal, activate the same virtual environment, and run:

```bash
python -m streamlit run frontend.py
```

Open the local URL printed in the terminal, usually [http://localhost:8501](http://localhost:8501).

### 7. Run the tests

```bash
python -m pytest -v
```

The project currently has 12 passing tests.

## Project structure

```text
ai-document-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── pdf_processor.py
│   └── search.py
├── tests/
│   ├── test_api.py
│   ├── test_main.py
│   ├── test_pdf_processor.py
│   └── test_search.py
├── frontend.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Current limitations

- The application stores the active document in memory, so uploaded documents do not persist after a backend restart.
- The current implementation is designed as a local prototype, not a multi-user production service.
- Scanned PDFs without an extractable text layer are not supported; OCR would be needed for those.
- Answers depend on the quality of the extracted text and the passages retrieved by semantic search.
- The local frontend configuration needs to be adjusted before deploying the application with a separately hosted backend.

## Possible improvements

- Support multiple documents and document collections.
- Add OCR for scanned PDFs.
- Improve retrieval with reranking and more advanced evaluation.
- Add user authentication and persistent storage.
- Deploy the frontend and backend with proper configuration and monitoring.

## License

No license has been added yet. If you want others to reuse or modify the code publicly, consider adding an appropriate open-source license.
