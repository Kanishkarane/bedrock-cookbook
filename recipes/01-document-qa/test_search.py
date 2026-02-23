"""
Test vector similarity search in OpenSearch
"""

import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from dotenv import load_dotenv

load_dotenv()

# Configuration
COLLECTION_ENDPOINT = ""
REGION = "us-east-1"
INDEX_NAME = "sec-filings"


def get_opensearch_client():
    credentials = boto3.Session().get_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        REGION,
        "aoss",
        session_token=credentials.token
    )
    
    return OpenSearch(
        hosts=[{"host": COLLECTION_ENDPOINT.replace("https://", ""), "port": 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def get_embedding(text: str) -> list:
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    body = json.dumps({"inputText": text})
    response = client.invoke_model(modelId="amazon.titan-embed-text-v1", body=body)
    return json.loads(response["body"].read())["embedding"]


def search(query: str, k: int = 3):
    """
    Search for similar documents.
    """
    os_client = get_opensearch_client()
    query_embedding = get_embedding(query)
    
    search_body = {
        "size": k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": k
                }
            }
        }
    }
    
    response = os_client.search(index=INDEX_NAME, body=search_body)
    return response["hits"]["hits"]


if __name__ == "__main__":
    test_queries = [
        "What are Amazon's main revenue sources?",
        "What risks does Amazon face?",
        "How much did AWS grow?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print("="*60)
        
        results = search(query, k=2)
        
        for i, hit in enumerate(results):
            print(f"\n--- Result {i+1} (score: {hit['_score']:.4f}) ---")
            print(hit["_source"]["text"][:300] + "...")