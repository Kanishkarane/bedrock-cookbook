"""
Basic structured extraction - learn the fundamentals
"""

import boto3
import json
from dotenv import load_dotenv

load_dotenv()

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-pro-v1:0"


def extract_structured(text: str, schema: dict, instructions: str) -> dict:
    """
    Extract structured data from text according to a schema.
    
    Args:
        text: The source text to extract from
        schema: JSON schema describing what to extract
        instructions: Additional instructions for extraction
        
    Returns:
        Extracted data as a dictionary
    """
    client = boto3.client("bedrock-runtime", region_name=REGION)
    
    prompt = f"""You are a data extraction assistant. Extract information from the provided text and return it as JSON.

<schema>
{json.dumps(schema, indent=2)}
</schema>

<instructions>
{instructions}
</instructions>

<text>
{text}
</text>

Return ONLY valid JSON matching the schema. No explanation, no markdown, just the JSON object."""

    body = json.dumps({
        "messages":[
            {
                "role":"user",
                "content":[{"text": prompt}]
            }

        ]
    })
    
    response = client.invoke_model(modelId=MODEL_ID, body=body)
    response_body = json.loads(response["body"].read())
    response_text = response_body["output"]["message"]["content"][0]["text"]
    
    # Parse JSON from response
    try:
        # Handle potential markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        return json.loads(response_text.strip())
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON: {e}", "raw_response": response_text}


# Test with sample text
if __name__ == "__main__":
    # Sample text from an SEC filing
    sample_text = """
    Amazon.com, Inc. reported net sales of $514 billion for the fiscal year ended 
    December 31, 2022, representing an increase of 9% compared to $469.8 billion 
    in 2021. Operating income decreased to $12.2 billion in 2022 from $24.9 billion 
    in 2021. The company employed approximately 1,541,000 full-time and part-time 
    employees as of December 31, 2022. Andy Jassy serves as President and Chief 
    Executive Officer.
    """
    
    # Define what we want to extract
    schema = {
        "company_name": "string",
        "fiscal_year": "number",
        "net_sales_billions": "number",
        "operating_income_billions": "number",
        "employee_count": "number",
        "ceo_name": "string"
    }
    
    instructions = """
    - Extract exact values from the text
    - Convert all monetary values to billions (e.g., $514 billion = 514)
    - If a value is not found, use null
    - For employee count, use the approximate number given
    """
    
    print("Extracting structured data...\n")
    result = extract_structured(sample_text, schema, instructions)
    
    print("Result:")
    print(json.dumps(result, indent=2))