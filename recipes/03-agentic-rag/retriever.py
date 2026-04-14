"""
Retriever - reusable search class for SEC filings
"""

import boto3
import json
import os
from dataclasses import dataclass
from typing import List
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from dotenv import load_dotenv

load_dotenv()

COLLECTION_ENDPOINT = os.getenv("COLLECTION_ENDPOINT")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
INDEX_NAME = "sec-filings"


@dataclass
class Chunk:
    text: str
    file: str
    score: float


class Retriever:
    def __init__(self):
        credentials = boto3.Session().get_credentials()
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

        self.bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    def embed(self, text: str) -> list:
        body = json.dumps({"inputText": text})
        response = self.bedrock.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=body
        )
        return json.loads(response["body"].read())["embedding"]

    def retrieve(self, query: str, k: int = 5) -> List[Chunk]:
        query_embedding = self.embed(query)

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

        response = self.opensearch.search(index=INDEX_NAME, body=search_body)

        chunks = []
        for hit in response["hits"]["hits"]:
            chunks.append(Chunk(
                text=hit["_source"].get("text", ""),
                file=hit["_source"].get("source_file", "unknown"),
                score=hit["_score"]
            ))

        return chunks