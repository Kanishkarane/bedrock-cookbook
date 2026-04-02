"""
Embed document chunks and store in OpenSearch
"""

import boto3
import json
from pathlib import Path
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from dotenv import load_dotenv

load_dotenv()

# Configuration - UPDATE THESE
COLLECTION_ENDPOINT = ""
REGION = "us-east-1"
INDEX_NAME = "sec-filings"

CHUNKS_DIR = Path("data/chunks")


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
        connection_class=RequestsHttpConnection,
        timeout=60,
        max_retries=3,
        retry_on_timeout=True
    )

    return client


def create_index(os_client):
    """Create index with correct knn_vector mapping."""
    if os_client.indices.exists(index=INDEX_NAME):
        os_client.indices.delete(index=INDEX_NAME)
        print(f"Deleted existing index: {INDEX_NAME}")

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
                    "dimension": 1536
                },
                "text": {"type": "text"},
                "source_file": {"type": "keyword"},
                "chunk_index": {"type": "integer"}
            }
        }
    }

    os_client.indices.create(index=INDEX_NAME, body=index_body)
    print(f"Created index: {INDEX_NAME}\n")


def get_embedding(text: str) -> list:
    """
    Get embedding using Bedrock Titan.
    """
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    body = json.dumps({"inputText": text[:10000]})

    response = client.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=body
    )

    response_body = json.loads(response["body"].read())
    return response_body["embedding"]


def index_chunks(os_client, chunks_file: Path):
    """
    Embed and index all chunks from a file.
    """
    with open(chunks_file, "r") as f:
        data = json.load(f)

    source_file = data["source_file"]
    chunks = data["chunks"]

    print(f"Indexing {len(chunks)} chunks from {chunks_file.name}...")

    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk["text"])

        doc = {
            "text": chunk["text"],
            "embedding": embedding,
            "source_file": source_file,
            "chunk_index": i
        }

        import time
        for attempt in range(3):
            try:
                os_client.index(
                    index=INDEX_NAME,
                    body=doc,
                )
                break
            except Exception as e:
                if attempt < 2:
                    print(f"  Retry {attempt + 1} for chunk {i}...")
                    time.sleep(2)
                else:
                    raise

        if (i + 1) % 10 == 0:
            print(f"  Indexed {i + 1}/{len(chunks)} chunks")

    print(f"  ✓ Completed {chunks_file.name}")


if __name__ == "__main__":
    print("Connecting to OpenSearch...")
    os_client = get_opensearch_client()

    create_index(os_client)

    chunk_files = list(CHUNKS_DIR.glob("*_chunks.json"))
    print(f"Found {len(chunk_files)} chunk files\n")

    for chunk_file in chunk_files:
        index_chunks(os_client, chunk_file)

    print("\n✓ All documents indexed!")