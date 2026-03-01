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


### Week 3: Streamlit Frontend

- Built RAG pipeline (`rag_pipeline.py`) combining Week 2 embeddings with Amazon Nova LLM
- Created Streamlit web interface for Q&A
- Added conversation history and source document display
- Implemented settings sidebar (number of sources, show/hide sources)

**What I learned:**
- How to build a web interface with Streamlit
- How to cache resources with `@st.cache_resource`
- How to manage session state in Streamlit
- End-to-end RAG: retrieve → generate → display

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
