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
```
