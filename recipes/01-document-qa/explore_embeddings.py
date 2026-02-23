"""
Explore embeddings - understand how text becomes vectors
"""

import boto3
import json
from dotenv import load_dotenv

load_dotenv()

def get_embedding(text: str) -> list:
    """
    Get embedding vector for a piece of text using Bedrock Titan.
    """
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    body = json.dumps({
        "inputText": text
    })
    
    response = client.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=body
    )
    
    response_body = json.loads(response["body"].read())
    return response_body["embedding"]


def cosine_similarity(vec1: list, vec2: list) -> float:
    """
    Calculate cosine similarity between two vectors.
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    return dot_product / (magnitude1 * magnitude2)


if __name__ == "__main__":
    # Test sentences
    sentences = [
        "Amazon reported strong revenue growth in Q4.",
        "The company's quarterly earnings exceeded expectations.",
        "I enjoy eating pizza on Friday nights.",
        "AWS cloud services saw increased adoption.",
    ]
    
    print("Getting embeddings for test sentences...\n")
    
    embeddings = {}
    for s in sentences:
        embeddings[s] = get_embedding(s)
        print(f"✓ Embedded: {s[:50]}...")
    
    print("\n" + "="*60)
    print("SIMILARITY SCORES")
    print("="*60 + "\n")
    
    # Compare first sentence to all others
    base = sentences[0]
    for s in sentences[1:]:
        similarity = cosine_similarity(embeddings[base], embeddings[s])
        print(f"'{base[:40]}...'")
        print(f"  vs '{s[:40]}...'")
        print(f"  Similarity: {similarity:.4f}\n")