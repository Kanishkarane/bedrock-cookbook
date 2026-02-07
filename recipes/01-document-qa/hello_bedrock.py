import boto3
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def call_claude(prompt: str) -> str:
    """
    Send a prompt to Claude via Amazon Bedrock and return the response.
    """
    # Create Bedrock runtime client
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    # Prepare the request
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    
    # Call Claude
    response = client.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=body
    )
    
    # Parse and return the response
    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]


if __name__ == "__main__":
    # Test prompt
    prompt = "Explain what RAG (Retrieval-Augmented Generation) is in 3 sentences."
    
    print("Sending prompt to Claude via Bedrock...")
    print(f"Prompt: {prompt}\n")
    
    response = call_claude(prompt)
    
    print("Response:")
    print(response)