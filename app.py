import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

st.set_page_config(page_title="Real Estate Due Diligence RAG", layout="centered")
st.title("🏡 Real Estate Due Diligence RAG (OpenAI)")

st.markdown(
    "Upload inspection reports, seller disclosures, appraisals, HOA documents, and more.\n\n"
    "Then chat with the documents to perform due diligence and generate investor-ready insights."
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---- Session State ----
if "vs_id" not in st.session_state:
    vs = client.vector_stores.create(name="real_estate_due_diligence_store")
    st.session_state.vs_id = vs.id

# Track which filenames we've indexed (session-only)
if "indexed_filenames" not in st.session_state:
    st.session_state.indexed_filenames = set()

# Chat history: list of {"role": "user"/"assistant", "content": "..."}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Selected model
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "gpt-5-mini"


def rag_call(messages, instructions):
    """
    Core RAG call: given messages + instructions,
    call Responses API with file_search pointed at our vector store.
    Returns (answer_text, used_files).
    """
    response = client.responses.create(
        model=st.session_state.model_choice,
        instructions=instructions,
        tools=[
            {
                "type": "file_search",
                "vector_store_ids": [st.session_state.vs_id],
            }
        ],
        input=messages,
    )

    answer_text = response.output_text or "_No text output._"

    used_files = []
    try:
        for block in response.output or []:
            for c in getattr(block, "content", []) or []:
                if getattr(c, "type", "") == "tool_result" and getattr(c, "tool_name", "") == "file_search":
                    for r in c.results or []:
                        if hasattr(r, "file_name"):
                            used_files.append(r.file_name)
    except Exception:
        pass

    return answer_text, sorted(set(used_files))


def ask_model(question: str, instructions: str, update_history: bool = True):
    """
    RAG helper for chat:
    - Build messages from chat_history + new question.
    - Call rag_call.
    - Optionally update chat_history.
    """
    messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.chat_history
    ]
    messages.append({"role": "user", "content": question})

    answer_text, used_files = rag_call(messages, instructions)

    if update_history:
        st.session_state.chat_history.append({"role": "user", "content": question})
        st.session_state.chat_history.append({"role": "assistant", "content": answer_text})

    return answer_text, used_files


# -----------------------------
# 1. Upload & Automatically Index Documents
# -----------------------------
st.subheader("1. Upload Real Estate Documents")

uploaded_files = st.file_uploader(
    "Upload PDFs, text files, or doc files (inspection, disclosures, HOA, appraisal, etc.)",
    accept_multiple_files=True,
)

newly_indexed_count = 0

if uploaded_files:
    with st.spinner("Indexing new documents…"):
        for f in uploaded_files:
            if f.name not in st.session_state.indexed_filenames:
                uploaded = client.files.create(
                    file=(f.name, f.read()),
                    purpose="assistants",
                )
                client.vector_stores.files.create(
                    vector_store_id=st.session_state.vs_id,
                    file_id=uploaded.id,
                )
                st.session_state.indexed_filenames.add(f.name)
                newly_indexed_count += 1

    if newly_indexed_count > 0:
        st.success(f"Indexed {newly_indexed_count} new document(s). You can now chat with them below. 👇")
    else:
        st.info("All uploaded documents are already indexed in this session.")

if st.session_state.indexed_filenames:
    st.caption(
        "Indexed documents: "
        + ", ".join(sorted(st.session_state.indexed_filenames))
    )
else:
    st.caption("No documents indexed yet. Upload files to begin.")


# -----------------------------
# 2. Model Selector
# -----------------------------
st.subheader("2. Model Selection")

st.session_state.model_choice = st.selectbox(
    "Choose a model",
    ["gpt-5-mini", "gpt-5-pro"],
    index=0 if st.session_state.model_choice == "gpt-5-mini" else 1,
)


# -----------------------------
# 3. Chat with the Documents
# -----------------------------
st.subheader("3. Chat with This Property's Documents")

if not st.session_state.indexed_filenames:
    st.info("Please upload at least one document before starting the chat.")
else:
    # Render chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    # Chat input
    follow_up = st.chat_input(
        "Ask a question about the property (e.g., 'What are the main risks with this property?')"
    )

    if follow_up:
        with st.spinner("Analyzing documents…"):
            instructions = (
                "You are a real estate due diligence analyst. "
                "Use ONLY the uploaded documents (inspection reports, seller disclosures, appraisals, "
                "HOA documents, etc.) to answer. Highlight major risks, estimated impact, and any "
                "missing information. When possible, reference the source filenames."
            )
            answer_text, used_files = ask_model(follow_up, instructions, update_history=True)

        # Force rerun so the new Q&A renders in the history loop
        st.rerun()


# -----------------------------
# 4. Investor Summary
# -----------------------------
st.subheader("4. Investor Summary")

st.markdown(
    "Generate an investor-style summary memo based on all uploaded documents. "
    "This is useful for a quick go/no-go or sharing with partners."
)

if not st.session_state.indexed_filenames:
    st.info("Upload and index documents first to generate an investor summary.")
else:
    if st.button("Generate Investor Summary"):
        with st.spinner("Generating investor summary…"):
            # For investor summary, we DON'T add another chat turn, but we
            # still give the model some context from the chat if it exists.
            messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.chat_history
            ]
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Create an investor-style memo for this property based ONLY on the uploaded documents. "
                        "Include the following sections:\n"
                        "1. High-Level Summary\n"
                        "2. Property Condition Overview\n"
                        "3. Major Risks (with severity)\n"
                        "4. Recommended Repairs / Capex Items\n"
                        "5. Potential Upside or Opportunities\n"
                        "6. Overall Recommendation (e.g., Buy / Cautious Buy / Pass)\n"
                    ),
                }
            )

            investor_instructions = (
                "You are a real estate investment analyst. "
                "Write clear, concise, investor-ready memos. "
                "Be specific and tie every claim back to the uploaded documents wherever possible."
            )

            investor_text, investor_files = rag_call(messages, investor_instructions)

        st.markdown("### Investor Memo")
        st.markdown(investor_text or "_No investor summary generated._")

        if investor_files:
            st.caption("Investor memo sources: " + ", ".join(investor_files))
