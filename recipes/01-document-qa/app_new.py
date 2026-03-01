"""
Amazon SEC Filings Q&A - Chat Interface
"""

import streamlit as st
from rag_pipeline import RAGPipeline
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Amazon SEC Q&A",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize RAG pipeline
@st.cache_resource
def load_pipeline():
    return RAGPipeline()

rag = load_pipeline()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "sources_history" not in st.session_state:
    st.session_state.sources_history = {}

# Sidebar
st.sidebar.header("⚙️ Settings")
num_chunks = st.sidebar.slider(
    "Number of sources",
    min_value=1,
    max_value=10,
    value=5
)

show_sources = st.sidebar.checkbox("Show sources", value=True)

st.sidebar.markdown("---")

# Clear chat button
if st.sidebar.button("🗑️ Clear chat"):
    st.session_state.messages = []
    st.session_state.sources_history = {}
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown(
    "Ask questions about Amazon using their SEC 10-K filings. "
    "Powered by Amazon Bedrock & OpenSearch."
)

# Main content
st.title("📊 Amazon SEC Q&A")

# Display chat history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show sources for assistant messages
        if message["role"] == "assistant" and show_sources:
            msg_id = message.get("id")
            if msg_id and msg_id in st.session_state.sources_history:
                sources = st.session_state.sources_history[msg_id]
                if sources:
                    with st.expander(f"📚 Sources ({len(sources)})"):
                        for source in sources:
                            st.markdown(f"**{source['file']}** (relevance: {source['score']:.2f})")
                            st.markdown(f"_{source['preview']}_")
                            st.markdown("---")

# Chat input
if query := st.chat_input("Ask about Amazon..."):
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            rag.num_chunks = num_chunks
            response = rag.ask(query)
        
        st.markdown(response.answer)
        
        # Store sources
        msg_id = f"msg_{len(st.session_state.messages)}"
        st.session_state.sources_history[msg_id] = response.sources
        
        # Show sources inline
        if show_sources and response.sources:
            with st.expander(f"📚 Sources ({len(response.sources)})"):
                for source in response.sources:
                    st.markdown(f"**{source['file']}** (relevance: {source['score']:.2f})")
                    st.markdown(f"_{source['preview']}_")
                    st.markdown("---")
    
    # Add assistant message to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response.answer,
        "id": msg_id
    })

# Show example questions if no chat history
if not st.session_state.messages:
    st.markdown("### 💡 Try asking:")
    
    examples = [
        "What are Amazon's main revenue sources?",
        "How fast is AWS growing?",
        "What risks does Amazon face?",
    ]
    
    cols = st.columns(len(examples))
    for i, (col, question) in enumerate(zip(cols, examples)):
        if col.button(question, key=f"ex_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()