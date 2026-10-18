
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="DocuMind",
    page_icon="D",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Session state ----------

defaults = {
    "uploaded": False,
    "document_name": "",
    "messages": [],
    "document_stats": {},
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- Styling ----------

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1050px;
        padding-top: 2.4rem;
        padding-bottom: 3rem;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .brand {
        font-size: 0.8rem;
        font-weight: 650;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--text-color);
        opacity: 0.65;
        margin-bottom: 1.3rem;
    }

    .page-title {
        font-size: 2.35rem;
        font-weight: 620;
        letter-spacing: -0.055em;
        line-height: 1.15;
        margin: 0 0 0.6rem 0;
        color: var(--text-color);
    }

    .page-description {
        font-size: 1rem;
        line-height: 1.65;
        max-width: 650px;
        opacity: 0.72;
        margin-bottom: 1.7rem;
    }

    .section-label {
        font-size: 0.76rem;
        font-weight: 650;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.62;
        margin-bottom: 0.5rem;
    }

    .document-card {
        padding: 0.9rem 1rem;
        border: 1px solid rgba(128, 128, 128, 0.28);
        border-radius: 8px;
        margin: 0.7rem 0 1rem 0;
    }

    .document-name {
        font-weight: 600;
        overflow-wrap: anywhere;
        margin-bottom: 0.25rem;
    }

    .document-detail {
        font-size: 0.83rem;
        opacity: 0.65;
    }

    [data-testid="stChatMessage"] {
        border: none;
        padding-top: 0.7rem;
        padding-bottom: 0.7rem;
    }

    [data-testid="stChatMessage"] p {
        line-height: 1.75;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.18);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    div[data-testid="stExpander"] {
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 8px;
    }

    div.stButton > button {
        border-radius: 7px;
        font-weight: 500;
        min-height: 2.5rem;
    }

    div[data-testid="stMetric"] {
        padding: 0.7rem 0;
    }

    .empty-state {
        padding: 2rem 0 1rem 0;
        max-width: 620px;
    }

    .empty-state h3 {
        font-size: 1.25rem;
        font-weight: 580;
        letter-spacing: -0.025em;
    }

    .muted {
        opacity: 0.68;
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Header ----------

st.markdown('<div class="brand">DOCUMIND / DOCUMENT READER</div>',
            unsafe_allow_html=True)

st.markdown(
    '<div class="page-title">Your documents, in context.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-description">
        Ask questions about a PDF, get answers based on its contents,
        and check the original passages whenever you need to.
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.uploaded:
    st.caption(f"Working with: {st.session_state.document_name}")
else:
    st.caption("No document loaded")


# ---------- Sidebar ----------

with st.sidebar:
    st.markdown("### Workspace")
    st.caption("DOCUMENT")

    pdf = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Text-based PDF, maximum 10 MB.",
        label_visibility="collapsed",
    )

    if st.button(
        "Process PDF",
        type="primary",
        disabled=pdf is None,
        use_container_width=True,
    ):
        with st.spinner("Extracting and indexing text..."):
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

                    st.rerun()
                else:
                    try:
                        detail = response.json().get(
                            "detail", "Could not process this PDF."
                        )
                    except ValueError:
                        detail = "Could not process this PDF."

                    st.error(detail)

            except requests.RequestException:
                st.error(
                    "Cannot connect to the backend. "
                    "Make sure FastAPI is running."
                )

    if st.session_state.uploaded:
        st.divider()
        st.caption("CURRENT DOCUMENT")

        st.markdown(
            f"""
            <div class="document-card">
                <div class="document-name">
                    {st.session_state.document_name}
                </div>
                <div class="document-detail">
                    Indexed and ready to query
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        stat1, stat2 = st.columns(2)
        stat1.metric(
            "Pages",
            st.session_state.document_stats.get("pages", 0),
        )
        stat2.metric(
            "Passages",
            st.session_state.document_stats.get("chunks", 0),
        )

        if st.button("New conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if st.button("Remove document", use_container_width=True):
            try:
                response = requests.post(
                    f"{API_URL}/clear",
                    timeout=10,
                )

                if response.ok:
                    st.session_state.uploaded = False
                    st.session_state.document_name = ""
                    st.session_state.document_stats = {}
                    st.session_state.messages = []
                    st.rerun()
                else:
                    st.error("Could not remove the document.")

            except requests.RequestException:
                st.error(
                    "Cannot connect to the backend. "
                    "Make sure FastAPI is running."
                )

    st.divider()
    st.caption("PDF extraction · Semantic search · Gemini")


# ---------- Main content ----------

if not st.session_state.uploaded:
    st.markdown('<div class="empty-state">', unsafe_allow_html=True)
    st.markdown("### Start with a document")
    st.markdown(
        """
        <p class="muted">
            Upload a PDF using the panel on the left. Once it has been
            processed, you can ask questions in plain language and
            inspect the passages used to form each answer.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.markdown("**The workflow**")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**01 — Add**")
        st.caption("Upload a PDF and extract its text.")

    with col2:
        st.markdown("**02 — Explore**")
        st.caption("Ask questions about the material.")

    with col3:
        st.markdown("**03 — Verify**")
        st.caption("Review source passages and page numbers.")

else:
    st.markdown('<div class="section-label">SUGGESTED QUESTIONS</div>',
                unsafe_allow_html=True)

    suggestions = [
        "Summarize the main points",
        "What are the key conclusions?",
        "Which important terms are defined?",
    ]

    suggestion_cols = st.columns(3)

    for index, suggestion in enumerate(suggestions):
        with suggestion_cols[index]:
            if st.button(suggestion, use_container_width=True):
                st.session_state.pending_question = suggestion
                st.rerun()

    st.divider()

    # Render previous messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            sources = message.get("sources", [])

            if sources:
                with st.expander(
                    f"Sources · {len(sources)} passages"
                ):
                    for source in sources:
                        st.markdown(
                            f"**Page {source['page_number']}** "
                            f"<span style='opacity:0.65'>"
                            f"· Similarity {source['score']:.3f}</span>",
                            unsafe_allow_html=True,
                        )
                        st.write(source["text"])
                        st.divider()

    pending_question = st.session_state.pop(
        "pending_question", None
    )

    typed_question = st.chat_input(
        "Ask about this document...",
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
            with st.spinner("Reading relevant passages..."):
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
                                "AI generation is unavailable. "
                                "Showing retrieved document passages."
                            )

                        if sources:
                            with st.expander(
                                f"Sources · {len(sources)} passages"
                            ):
                                for source in sources:
                                    st.markdown(
                                        f"**Page {source['page_number']}** "
                                        f"<span style='opacity:0.65'>"
                                        f"· Similarity "
                                        f"{source['score']:.3f}</span>",
                                        unsafe_allow_html=True,
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
                        try:
                            detail = response.json().get(
                                "detail",
                                "The question could not be answered.",
                            )
                        except ValueError:
                            detail = "The question could not be answered."

                        st.error(detail)

                except requests.RequestException:
                    st.error(
                        "Cannot connect to the backend. "
                        "Make sure FastAPI is running."
                    )
