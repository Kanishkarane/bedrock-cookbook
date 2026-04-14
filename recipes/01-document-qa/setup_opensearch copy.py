"""
Set up OpenSearch index for vector storage
"""
import os
import sys
import boto3
import json
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# Configuration - UPDATE THESE
COLLECTION_ENDPOINT = os.getenv("COLLECTION_ENDPOINT")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
INDEX_NAME = "sec-filings"

# Titan embedding dimension
EMBEDDING_DIMENSION = 1536


def get_opensearch_client():
    """
    Create OpenSearch client with AWS auth.
    """
    if not COLLECTION_ENDPOINT:
        raise ValueError("COLLECTION_ENDPOINT environment variable is not set.")

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


def validate_index(client):
    """
    Confirm the embedding field is correctly mapped as knn_vector.
    """
    mapping = client.indices.get_mapping(index=INDEX_NAME)
    props = mapping[INDEX_NAME]["mappings"]["properties"]
    embedding_type = props.get("embedding", {}).get("type")
    if embedding_type == "knn_vector":
        print(f"  ✓ 'embedding' field is correctly mapped as knn_vector")
    else:
        print(f"  ✗ 'embedding' field type is '{embedding_type}' — expected 'knn_vector'")
        print("    Run with --recreate to fix this.")


if __name__ == "__main__":
    recreate = "--recreate" in sys.argv

    print("Connecting to OpenSearch...")
    client = get_opensearch_client()
    print("✓ Connected\n")

    if client.indices.exists(index=INDEX_NAME):
        if recreate:
            print(f"Deleting existing index '{INDEX_NAME}'...")
            client.indices.delete(index=INDEX_NAME)
            print(f"✓ Deleted '{INDEX_NAME}'\n")
        else:
            print(f"Index '{INDEX_NAME}' already exists.")
            print("Validating mapping...")
            validate_index(client)
            print("\nTo recreate the index with the correct mapping, run:")
            print("  python setup_opensearch.py --recreate")
            sys.exit(0)

    print(f"Creating index '{INDEX_NAME}'...")
    response = create_index(client)
    print(f"✓ Index created: {response}\n")

    print("Validating mapping...")
    validate_index(client)