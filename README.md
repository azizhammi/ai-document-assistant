# DocuMind — AI Document Assistant

DocuMind is a PDF question-answering application that lets users upload a document, ask questions about its contents, and inspect the relevant passages and page references behind the answers.

The application combines semantic search with a language model to retrieve useful context before generating an answer. It includes a FastAPI backend, a Streamlit interface, automated tests, and a small retrieval evaluation benchmark.

I built this project to gain practical experience with Python, API development, semantic search, embedding models, retrieval-augmented generation (RAG), and language model integration.

## Features

- **PDF processing:** Extracts text from PDFs while preserving page references.
- **Semantic search:** Uses Sentence Transformers embeddings to find passages related to a question by meaning rather than exact keyword matches.
- **Retrieval-augmented question answering:** Uses retrieved document passages as context for Gemini-generated answers.
- **Source references:** Displays retrieved passages and page numbers to help users verify answers against the original document.
- **Retrieval-only fallback:** Continues to retrieve relevant passages when a Gemini API key is not configured.
- **Cached embeddings:** Reuses document chunk embeddings across questions to avoid repeatedly encoding the same passages.
- **Streamlit interface:** Includes PDF upload, suggested questions, chat history, document statistics, source inspection, and document reset controls.
- **Automated tests:** Covers PDF processing, semantic search, API behavior, and document handling.
- **Retrieval evaluation:** Includes a reproducible script and a small benchmark for measuring retrieval quality.

## Tech stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| FastAPI | Backend and REST API |
| Streamlit | Web interface |
| PyMuPDF | PDF text extraction |
| Sentence Transformers | Text embeddings |
| NumPy | Numerical and similarity calculations |
| Google Gemini API | Context-grounded answer generation |
| Pytest | Automated testing |
| HTTPX | API testing |
| python-dotenv | Local environment configuration |

## How it works

1. The user uploads a PDF through the Streamlit interface.
2. The FastAPI backend extracts the text and splits it into smaller, overlapping chunks, retaining page information.
3. Sentence Transformers converts the document chunks into vector embeddings.
4. When a question is submitted, the application embeds the question and ranks document passages by semantic similarity.
5. The most relevant passages are provided as context to Gemini, when an API key is configured.
6. The application displays the answer alongside the retrieved sources and page references.

Document embeddings are cached after the initial processing, allowing subsequent questions to reuse them instead of re-encoding the entire document.

If Gemini is not configured, the application falls back to showing relevant retrieved passages without generating a model-written answer.

## Getting started

### Requirements

- Python 3.11 or newer
- Git
- A Google Gemini API key for generated answers (optional)

The first run may take longer because the embedding model needs to be downloaded.

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

If PowerShell blocks environment activation, you can run the virtual environment's Python directly using `.venv\Scripts\python.exe`.

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Gemini (optional)

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Replace the placeholder with your own API key. The model setting can be changed to a supported Gemini model available to your account.

API usage may incur charges. Never commit your `.env` file or share your API key.

Without a configured Gemini API key, the application can still perform semantic retrieval and return relevant passages.

### 5. Start the backend

In the first terminal, activate the virtual environment if necessary, then run:

```bash
python -m uvicorn app.main:app --reload
```

The API documentation is available at:

http://127.0.0.1:8000/docs

### 6. Start the frontend

Open a second terminal in the project directory, activate the same virtual environment, and run:

```bash
python -m streamlit run frontend.py
```

Open the local URL printed in the terminal, usually:

http://localhost:8501

Keep the backend running while using the frontend.

### 7. Run the tests

```bash
python -m pytest -v
```

The test suite covers the main PDF processing, retrieval, and API functionality. Run the command above to see the current number of passing tests.

## Retrieval evaluation

DocuMind includes a small synthetic retrieval benchmark in `evaluation/benchmark.json` and an evaluation script at `scripts/evaluate_retrieval.py`.

Run it from the project root:

```bash
python scripts/evaluate_retrieval.py
```

The current benchmark results are:

| Metric | Result |
|---|---:|
| Mean Recall@3 | 1.000 |
| Mean Precision@3 | 0.375 |
| Mean Reciprocal Rank@3 (MRR@3) | 1.000 |

**Important:** These results come from a small benchmark of 8 questions over synthetic document chunks. They are useful for checking the retrieval implementation, but they do not establish performance on real-world documents or a representative evaluation dataset.

- **Recall@3** measures how many relevant chunks are retrieved within the top three results.
- **Precision@3** measures the proportion of the top three retrieved chunks that are relevant.
- **MRR@3** measures how highly the first relevant result ranks, considering only the top three results.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Root endpoint |
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Upload and process a PDF |
| `POST` | `/ask` | Ask a question about the active document |
| `POST` | `/clear` | Clear the active document state |

Interactive API documentation is available at `http://127.0.0.1:8000/docs` while the backend is running.

## Project structure

```text
ai-document-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── pdf_processor.py
│   └── search.py
├── evaluation/
│   └── benchmark.json
├── scripts/
│   └── evaluate_retrieval.py
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

- **In-memory document state:** The active document and its embeddings are held in backend memory and are lost when the backend restarts.
- **Single active document:** The current global state is intended for a local prototype and is not isolated between users. It is not suitable for concurrent multi-user use without architectural changes.
- **Text-based PDFs:** Scanned PDFs without an extractable text layer require OCR, which is not currently implemented.
- **Retrieval quality:** Answers depend on the extracted text and the relevance of the retrieved passages.
- **Model dependency:** Generated answers require a valid Gemini API key and access to the configured model.
- **Local configuration:** The frontend defaults to `http://127.0.0.1:8000`. For deployment, configure the backend URL appropriately and host the backend separately.
- **Limited evaluation:** The included benchmark is small and synthetic; broader testing is needed to assess retrieval quality on diverse real-world documents.

## Possible improvements

- Support multiple documents and document collections.
- Add OCR for scanned PDFs.
- Improve retrieval with reranking, hybrid search, and a larger evaluation dataset.
- Add user authentication and per-user document isolation.
- Introduce persistent storage for documents and embeddings.
- Add integration tests for end-to-end document question answering.
- Deploy the frontend and backend with environment-based configuration, monitoring, and production-ready security controls.

## License

No license has been added yet. Until a license is selected, others should not assume they have permission to reuse, modify, or redistribute this project. Consider adding an appropriate open-source license if you want to allow public reuse.