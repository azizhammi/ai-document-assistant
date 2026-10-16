
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="DocuMind | AI Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Session state ----------

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "document_name" not in st.session_state:
    st.session_state.document_name = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "document_stats" not in st.session_state:
    st.session_state.document_stats = {}


# ---------- Styling ----------

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 1.5rem 1.7rem;
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        margin-bottom: 0.4rem;
        font-size: 2.1rem;
    }
    .hero p {
        margin-bottom: 0;
        opacity: 0.8;
    }
    [data-testid="stChatMessage"] {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Header ----------

st.markdown(
    """
    <div class="hero">
        <h1>📚 DocuMind</h1>
        <p>Your documents, understood. Upload a PDF and ask questions
        with answers grounded in its content.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([2, 1])

with left:
    st.subheader("Ask your document")
    st.caption(
        "Get answers from your PDF and inspect the passages "
        "used to support them."
    )

with right:
    if st.session_state.uploaded:
        st.success(f"Ready: {st.session_state.document_name}")
    else:
        st.info("Upload a PDF to get started")


# ---------- Sidebar ----------

with st.sidebar:
    st.header("📄 Your document")

    pdf = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
        help="Use a text-based PDF smaller than 10 MB.",
    )

    if st.button(
        "Process document",
        type="primary",
        disabled=pdf is None,
        use_container_width=True,
    ):
        with st.spinner("Reading and indexing your PDF..."):
            try:
                response = requests.post(
                    f"{API_URL}/upload",
                    files={
                        "file": (
                            pdf.name,
                            pdf.getvalue(),
                            "application/pdf",
                        )
                    },
                    timeout=120,
                )

                if response.ok:
                    result = response.json()

                    st.session_state.uploaded = True
                    st.session_state.document_name = pdf.name
                    st.session_state.messages = []
                    st.session_state.document_stats = {
                        "pages": result["pages_with_text"],
                        "chunks": result["chunks_created"],
                    }

                    st.success("Document processed successfully!")
                    st.rerun()
                else:
                    detail = response.json().get(
                        "detail", "Could not process the PDF."
                    )
                    st.error(detail)

            except requests.RequestException:
                st.error(
                    "Cannot reach the backend. Start FastAPI in "
                    "another terminal and try again."
                )

    if st.session_state.uploaded:
        st.divider()
        st.markdown("**Current document**")
        st.write(st.session_state.document_name)

        stat1, stat2 = st.columns(2)
        stat1.metric(
            "Pages",
            st.session_state.document_stats.get("pages", 0),
        )
        stat2.metric(
            "Text chunks",
            st.session_state.document_stats.get("chunks", 0),
        )

        if st.button("Reset chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if st.button("Clear document", use_container_width=True):
            # The backend stores one document globally. Clear it through
            # a dedicated endpoint, which we'll add in the next step.
            st.warning(
                "The backend does not have a document-clear endpoint yet. "
                "We'll add one next."
            )

    st.divider()
    st.caption("Built with Streamlit, FastAPI and semantic search.")


# ---------- Suggested questions ----------

if not st.session_state.uploaded:
    st.markdown("### How it works")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 1. Upload")
        st.write("Choose a text-based PDF from your computer.")

    with col2:
        st.markdown("#### 2. Ask")
        st.write("Ask a specific question about the document.")

    with col3:
        st.markdown("#### 3. Verify")
        st.write("Inspect the source passages and page numbers.")

    st.info("Upload a PDF in the sidebar to begin.")

else:
    suggestions = [
        "Summarize the main points",
        "What are the key conclusions?",
        "What important terms are defined?",
    ]

    st.markdown("**Try asking**")

    suggestion_cols = st.columns(3)

    for index, suggestion in enumerate(suggestions):
        with suggestion_cols[index]:
            if st.button(suggestion, use_container_width=True):
                st.session_state.pending_question = suggestion
                st.rerun()


# ---------- Chat history ----------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        sources = message.get("sources", [])

        if sources:
            with st.expander(
                f"📎 View {len(sources)} retrieved source passages"
            ):
                for source in sources:
                    st.markdown(
                        f"**Page {source['page_number']}** · "
                        f"Similarity: {source['score']:.3f}"
                    )
                    st.write(source["text"])
                    st.divider()


# ---------- Question handling ----------

pending_question = st.session_state.pop("pending_question", None)
typed_question = st.chat_input(
    "Ask a question about your document...",
    disabled=not st.session_state.uploaded,
)
question = typed_question or pending_question

if question and st.session_state.uploaded:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the document and preparing an answer..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=120,
                )

                if response.ok:
                    result = response.json()
                    answer = result["answer"]
                    sources = result.get("sources", [])

                    st.markdown(answer)

                    if result.get("mode") == "retrieval_only":
                        st.caption(
                            "Retrieval-only mode: configure an API key "
                            "to enable generated answers."
                        )

                    with st.expander(
                        f"📎 View {len(sources)} retrieved source passages"
                    ):
                        for source in sources:
                            st.markdown(
                                f"**Page {source['page_number']}** · "
                                f"Similarity: {source['score']:.3f}"
                            )
                            st.write(source["text"])
                            st.divider()

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )
                else:
                    detail = response.json().get(
                        "detail", "The question could not be answered."
                    )
                    st.error(detail)

            except requests.RequestException:
                st.error(
                    "Cannot reach the backend. Check that FastAPI is running."
                )
