import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Fix path so Python can find sec_tools.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from sec_tools import ALL_TOOLS

# ── Agent setup ───────────────────────────────────────────
SYSTEM_PROMPT = """You are a financial analyst assistant specializing in Amazon's SEC filings.

You have access to tools that can:
1. Search Amazon's 10-K SEC filings for specific information
2. Extract structured financial data (revenue, income, segments)
3. Extract and categorize risk factors
4. Extract executive/leadership information

Guidelines:
- Use tools when you need specific data from the filings
- For simple factual questions, search first then answer
- For structured data requests, use the extract tools
- Always cite which filing year your information comes from when possible
- If you can't find information, say so clearly
- Be concise but accurate

You do NOT need to use tools for:
- General knowledge questions about Amazon
- Explaining financial concepts
- Calculations on data you've already retrieved"""


def create_agent():
    conversation_manager = SlidingWindowConversationManager(window_size=10)
    return Agent(
        model='amazon.nova-pro-v1:0',
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        conversation_manager=conversation_manager
    )

def get_callback_handler(tools_used: list):
    def callback_handler(**kwargs):
        if "current_tool_use" in kwargs:
            tool_name = kwargs["current_tool_use"]["name"]
            if tool_name not in tools_used:
                tools_used.append(tool_name)
    return callback_handler

# ── Streamlit UI ──────────────────────────────────────────
st.set_page_config(page_title="SEC Filing Agent", page_icon="📄")
st.title("📄 Amazon SEC Filing Agent")

# ── Session state ─────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = create_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_tools_used" not in st.session_state:
    st.session_state.last_tools_used = []

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💡 Example Questions")
    st.markdown("""
    - What are Amazon's main risk factors?
    - Show me AWS revenue breakdown
    - Who are Amazon's key executives?
    - What were Amazon's financials in 2023?
    """)

    st.markdown("---")

    st.markdown("### 🔧 Last Query Tools Used")
    if st.session_state.last_tools_used:
        for tool in st.session_state.last_tools_used:
            st.markdown(f"- `{tool}`")
    else:
        st.caption("No tools used yet.")

    st.markdown("---")

    st.markdown("### 🛠️ Available Tools")
    st.markdown("""
    - `search_sec_filings` — search filings
    - `extract_financials` — revenue, income
    - `extract_risks` — risk factors
    - `extract_executives` — leadership info
    """)

    if st.button("🗑️ Clear Conversation"):
        st.session_state.agent = create_agent()
        st.session_state.messages = []
        st.session_state.last_tools_used = []
        st.rerun()

# ── Replay chat history ───────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
    if "tools_used" in msg:
        st.caption(f"🔧 Tools used: {', '.join(msg['tools_used'])}")

# ── Chat input + agent call ───────────────────────────────
if prompt := st.chat_input("Ask about Amazon's filings..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            tools_used = []
            response = st.session_state.agent(
                prompt,
                callback_handler=get_callback_handler(tools_used)
            )
            response_text = str(response)
            st.session_state.last_tools_used = tools_used
        st.markdown(response_text)
        if tools_used:
            st.caption(f"🔧 Tools used: {', '.join(tools_used)}")

    # Store response + tools used
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "tools_used": tools_used
    })
    st.session_state.last_tools_used = tools_used
    st.rerun()