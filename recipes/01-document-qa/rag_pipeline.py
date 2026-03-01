"""
RAG Pipeline - combines Week 2 (embeddings + OpenSearch) with Week 1 (Bedrock/Claude)
"""

import boto3
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from dotenv import load_dotenv

load_dotenv()

COLLECTION_ENDPOINT = os.getenv("COLLECTION_ENDPOINT", "your-collection-endpoint-here")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
INDEX_NAME = "sec-filings"


@dataclass
class RAGResponse:
    answer: str
    sources: List[Dict] = field(default_factory=list)


class RAGPipeline:
    def __init__(self):
        self.num_chunks = 5

        self.bedrock = boto3.client(
            "bedrock-runtime",
            region_name=REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

        credentials = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=REGION
        ).get_credentials()

        auth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            REGION,
            "aoss",
            session_token=credentials.token
        )

        self.opensearch = OpenSearch(
            hosts=[{"host": COLLECTION_ENDPOINT.replace("https://", ""), "port": 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

    def embed_query(self, text: str) -> list:
        """Embed query using Titan"""
        if not text or not text.strip():
            raise ValueError("Cannot embed an empty query")

        response = self.bedrock.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=json.dumps({"inputText": text.strip()})
        )
        return json.loads(response["body"].read())["embedding"]

    def search(self, query: str) -> List[Dict]:
        """Search OpenSearch"""
        query_embedding = self.embed_query(query)

        search_body = {
            "size": self.num_chunks,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": self.num_chunks
                    }
                }
            }
        }

        response = self.opensearch.search(index=INDEX_NAME, body=search_body)

        sources = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            file_display = Path(source.get("source_file", "unknown")).name
            sources.append({
                "file": file_display,
                "score": hit["_score"],
                "preview": source.get("text", "")[:300],
                "text": source.get("text", "")
            })

        return sources

    def ask(self, query: str) -> RAGResponse:
        """Full RAG: retrieve relevant chunks, then ask Claude"""
        query = query.strip()
        if not query:
            return RAGResponse(answer="Please enter a question.", sources=[])

        sources = self.search(query)

        if not sources:
            return RAGResponse(
                answer="I couldn't find relevant information in the documents to answer your question.",
                sources=[]
            )

        context = "\n\n---\n\n".join([s["text"] for s in sources])

        prompt = f"""You are an expert analyst of Amazon's SEC filings.

Use the following excerpts from Amazon's 10-K filings to answer the question.
Be specific and cite numbers/figures when available.
If the answer isn't in the excerpts, say so clearly — do not make things up.

Context from SEC filings:
{context}

Question: {query}

Answer:"""

        response = self.bedrock.invoke_model(
            modelId="us.amazon.nova-pro-v1:0",
            body=json.dumps({
            "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
            ]
        }))

        response_body = json.loads(response["body"].read())
        answer = response_body["output"]["message"]["content"][0]["text"]

        return RAGResponse(answer=answer, sources=sources)