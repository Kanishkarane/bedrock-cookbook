# Bedrock Cookbook

Production-ready recipes for building applications with Amazon Bedrock.

## About This Project

This is an open-source collection of working examples that demonstrate how to build real applications using Amazon Bedrock and Claude. Each recipe is designed to be:

- **Production-ready** — Not just demos, but code you can build on
- **Well-documented** — Clear explanations of what and why
- **Educational** — Learn by doing

## Recipes

### 01 - Document Q&A with RAG
Build a question-answering system that retrieves relevant information from documents and generates accurate answers.

Status: 🚧 In Progress

## Progress

### Week 1: Foundation & First Bedrock Call

- Created public GitHub repository with proper project structure
- Set up AWS account with Bedrock model access
- Created IAM user with programmatic access
- Successfully called Claude via Amazon Bedrock API

**What I learned:**
- How to configure AWS credentials securely using .env files
- How to use boto3 to interact with Amazon Bedrock
- How RAG (Retrieval-Augmented Generation) works at a high level
- Proper project structure for a production Python project

### Week 2: Embeddings & Vector Storage

- Downloaded Amazon 10-K SEC filings (3 years) from SEC EDGAR
- Implemented document chunking (500 words, 50 word overlap) — 233 chunks total
- Created embeddings using Amazon Titan (amazon.titan-embed-text-v1)
- Stored vectors in Amazon OpenSearch Serverless
- Tested similarity search with financial queries

**What I learned:**
- Embeddings convert text into numerical vectors where semantic similarity maps to mathematical proximity — business sentences scored higher similarity with each other than unrelated topics
- AWS OpenSearch Serverless requires three separate policies (encryption, network, data access) plus IAM permissions — missing any one causes 403 errors
- Chunking documents with overlap (50 words) preserves context at boundaries, preventing important information from being split across chunks
- OpenSearch Serverless has API differences from regular OpenSearch — custom document IDs and manual index refresh are not supported


### Week 3 & 4 : Streamlit Frontend & Rag pipeline

- Built RAG pipeline (`rag_pipeline.py`) combining Week 2 embeddings with Amazon Nova LLM
- Created Streamlit web interface for Q&A
- Added conversation history and source document display
- Implemented settings sidebar (number of sources, show/hide sources)

**What I learned:**
- How to build a web interface with Streamlit
- How to cache resources with `@st.cache_resource`
- How to manage session state in Streamlit
- End-to-end RAG: retrieve → generate → display

Week 5:
## Recipe 02: Structured Data Extraction

Extract structured JSON data from unstructured SEC filing text.

### What it extracts

- **Financials**: Revenue, operating income, net income, business segments
- **Risks**: Categorized risk factors with summaries
- **Executives**: Names, titles, ages, tenure

### How it works

1. Uses the retriever from Recipe 01 to find relevant text chunks
2. Sends chunks to Claude with a specific extraction schema
3. Parses JSON response and validates the data
4. Combines into a complete company profile

### Files

- `basic_extraction.py` - Simple extraction example
- `extractors.py` - Specialized extractors for different data types
- `extraction_pipeline.py` - End-to-end pipeline
- `validators.py` - Data validation helpers

### Usage
```python
from extraction_pipeline import ExtractionPipeline

pipeline = ExtractionPipeline()
profile = pipeline.extract_company_profile("Amazon")
profile.save("amazon_profile.json")
```

### Example output
```json
{
  "company": "Amazon",
  "financials": {
    "revenue": {"amount_billions": 514, "year": 2022}
  },
  "risks": [
    {"category": "Competitive", "title": "Intense competition", "summary": "..."}
  ],
  "executives": [
    {"name": "Andy Jassy", "title": "CEO"}
  ]
}
```

### What I learned
- Extraction returns structured JSON instead of free text — better for databases, dashboards, and comparisons
- Schema-based prompting: give the LLM a template to fill in, not just a question to answer
- Always clean LLM responses before parsing JSON — models sometimes wrap output in code blocks
- Single responsibility architecture: retriever fetches, extractor extracts, validator checks, pipeline orchestrates
- Never trust LLM output blindly — validate ranges, required fields, and impossible values

  
Week 6 :

## Recipe 03: Agentic RAG with Strands

An intelligent agent that autonomously decides how to answer questions about Amazon's SEC filings.

### What makes it agentic?

Unlike the fixed RAG pipeline in Recipe 01, this agent:
- **Reasons** about what information it needs
- **Chooses** which tool to use (or no tool at all)
- **Iterates** if the first approach doesn't work
- **Maintains context** across a conversation

### Tools available to the agent

| Tool                 | Purpose                             |
| `search_sec_filings` | Semantic search over 10-K documents |
| `extract_financials` | Pull structured financial metrics   |
| `extract_risks`      | Extract categorized risk factors    |
| `extract_executives` | Get leadership information          |

### Files

- `sec_tools.py` - Tool definitions wrapping existing code
- `sec_agent.py` - Main agent with system prompt
- `hello_strands.py` - Basic Strands introduction
- `agent_with_tool.py` - Simple tool example

### Usage
```python
from sec_agent import create_agent

agent = create_agent()
response = agent("What are Amazon's main risks?")
print(response)
```

### What I learned

- Agents dynamically **reason about which tool to use** based on the question — unlike Recipe 01 where the flow was always retrieve → generate
- **Tool docstrings are the agent's instructions** — the agent reads them to decide when to call each tool, so vague docstrings lead to wrong tool choices
- Setting up OpenSearch correctly matters — **index mappings must define `knn_vector` upfront** or vector search silently breaks
- **Conversation memory** via `SlidingWindowConversationManager` is what enables follow-up questions — without it the agent treats every message as a fresh conversation
- Tools are just **regular Python functions** wrapped with `@tool` — your existing retriever and extractor code needed almost no changes
- The agent **skips tools entirely** for general knowledge questions like "what does SEC stand for?" — it only calls tools when it genuinely needs data
- When the agent picks the **wrong tool**, the fix is in the docstring — not the code itself

Week 7:

## Recipe 03: Streamlit UI for Agentic RAG

A chat interface for the SEC Filing Agent from Week 6, built with Streamlit.

### What it does

- Chat with the SEC agent in natural language
- Shows which tools the agent used per response (e.g. `search_sec_filings`, `extract_risks`)
- Example question buttons so users know what to ask
- Formats JSON responses with `st.json()`
- Clear conversation button

### Files

- `app.py` - Main Streamlit chat interface
- `sec_agent.py` - Agent definition (from Week 6)
- `sec_tools.py` - Tool definitions (from Week 6)

### Usage
```bash
streamlit run recipes/03-agentic-rag/app.py
```

### What I learned

- `st.session_state` is essential — initialize the agent once, not on every rerender
- Tool usage is best captured via a callback handler wrapping the agent, not by parsing response text
- Streamlit Cloud doesn't read `.env` files — AWS credentials must be added as Streamlit Secrets
- When modules live across multiple folders, the cleanest fix is to copy dependencies into the same directory as `app.py` rather than fighting `sys.path`
 
## Setup

### Prerequisites
- Python 3.9+
- AWS Account with Bedrock access
- Claude model access enabled in Bedrock

### Installation

1. Clone this repository
```bash
   git clone https://github.com/YOUR_USERNAME/bedrock-cookbook.git
   cd bedrock-cookbook
```

2. Install dependencies
```bash
   pip install -r requirements.txt
```

3. Configure AWS credentials
```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
```

4. Test your setup
```bash
   python recipes/01-document-qa/hello_bedrock.py
```

## Author

**Kanishka** — B.Tech AI & Data Science, SNU Chennai

## License

MIT License