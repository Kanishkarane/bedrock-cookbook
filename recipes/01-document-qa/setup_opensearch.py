"""
Set up OpenSearch index for vector storage
"""

import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Configuration - UPDATE THESE
COLLECTION_ENDPOINT = ""  # e.g., https://xxxxx.us-east-1.aoss.amazonaws.com
REGION = "us-east-1"
INDEX_NAME = "sec-filings"

# Titan embedding dimension
EMBEDDING_DIMENSION = 1536


def get_opensearch_client():
    """
    Create OpenSearch client with AWS auth.
    """
    credentials = boto3.Session().get_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        REGION,
        "aoss",
        session_token=credentials.token
    )
    
    client = OpenSearch(
        hosts=[{"host": COLLECTION_ENDPOINT.replace("https://", ""), "port": 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    return client


def create_index(client):
    """
    Create index with vector field mapping.
    """
    index_body = {
        "settings": {
            "index": {
                "knn": True
            }
        },
        "mappings": {
            "properties": {
                "embedding": {
                    "type": "knn_vector",
                    "dimension": EMBEDDING_DIMENSION,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "faiss"
                    }
                },
                "text": {
                    "type": "text"
                },
                "source_file": {
                    "type": "keyword"
                },
                "chunk_index": {
                    "type": "integer"
                }
            }
        }
    }
    
    response = client.indices.create(index=INDEX_NAME, body=index_body)
    return response


if __name__ == "__main__":
    print("Connecting to OpenSearch...")
    client = get_opensearch_client()
    
    # Check if index exists
    if client.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists")
    else:
        print(f"Creating index '{INDEX_NAME}'...")
        response = create_index(client)
        print(f"✓ Index created: {response}")