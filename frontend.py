
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📄",
    layout="wide",
)

st.title("📄 AI Document Assistant")
st.caption("Upload a PDF and ask questions about its contents.")

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Your document")

    pdf = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
    )

    if st.button("Upload PDF", disabled=pdf is None):
        with st.spinner("Processing your PDF..."):
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
                    st.session_state.messages = []
                    st.success("PDF uploaded successfully!")
                    st.write(
                        f"Pages with text: {result['pages_with_text']}"
                    )
                    st.write(f"Chunks created: {result['chunks_created']}")
                else:
                    st.error(response.json().get("detail", "Upload failed."))

            except requests.RequestException:
                st.error(
                    "Could not connect to the backend. "
                    "Make sure FastAPI is running."
                )

    if st.session_state.uploaded:
        st.success("Document ready for questions")

st.divider()

# Display previous messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("View source passages"):
                for source in message["sources"]:
                    st.markdown(
                        f"**Page {source['page_number']}** "
                        f"(similarity: {source['score']:.3f})"
                    )
                    st.write(source["text"])

question = st.chat_input(
    "Ask a question about your PDF...",
    disabled=not st.session_state.uploaded,
)

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Finding an answer..."):
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

                    with st.expander("View source passages"):
                        for source in sources:
                            st.markdown(
                                f"**Page {source['page_number']}** "
                                f"(similarity: {source['score']:.3f})"
                            )
                            st.write(source["text"])

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                        }
                    )
                else:
                    st.error(
                        response.json().get(
                            "detail", "The question failed."
                        )
                    )

            except requests.RequestException:
                st.error(
                    "Could not connect to the backend. "
                    "Make sure FastAPI is running."
                )
