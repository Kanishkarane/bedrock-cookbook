"""
Amazon SEC Filings Q&A - Streamlit Interface
"""
import streamlit as st
from rag_pipeline import RAGPipeline

st.set_page_config(
    page_title="Amazon SEC Q&A",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_pipeline():
    return RAGPipeline()

rag = load_pipeline()

# Initialize session state for query
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""

# Sidebar
st.sidebar.header("⚙️ Settings")
num_chunks = st.sidebar.slider(
    "Number of sources to retrieve",
    min_value=1,
    max_value=10,
    value=5,
    help="More sources = more context, but slower and more expensive"
)

show_sources = st.sidebar.checkbox("Show source documents", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown(
    "This app answers questions about Amazon using their SEC 10-K filings. "
    "Built with Amazon Bedrock and OpenSearch."
)

# Main content
st.title("📊 Amazon SEC Filings Q&A")
st.markdown("Ask questions about Amazon's business, financials, risks, and operations.")

# Question input — uses pending_query as default value
query = st.text_input(
    "Your question:",
    value=st.session_state.pending_query,
    placeholder="e.g., What are Amazon's main revenue sources?",
)

# Submit button
if st.button("Ask", type="primary", disabled=not query):
    with st.spinner("Searching documents and generating answer..."):
        rag.num_chunks = num_chunks
        response = rag.ask(query)
    
    st.markdown("### Answer")
    st.markdown(response.answer)
    
    if show_sources and response.sources:
        st.markdown("---")
        st.markdown(f"### Sources ({len(response.sources)} documents)")
        
        for i, source in enumerate(response.sources, 1):
            with st.expander(f"📄 {source['file']} (relevance: {source['score']:.2f})"):
                st.markdown(source['preview'])

# Example questions
st.markdown("---")
st.markdown("### 💡 Example questions")

example_questions = [
    "What are Amazon's main sources of revenue?",
    "How fast is AWS growing?",
    "What are the biggest risks Amazon faces?",
    "What is Amazon's approach to sustainability?",
    "How many employees does Amazon have?",
]

cols = st.columns(2)
for i, question in enumerate(example_questions):
    col = cols[i % 2]
    if col.button(question, key=f"example_{i}", use_container_width=True):
        st.session_state.pending_query = question  # ✅ separate variable, not widget key
        st.rerun()