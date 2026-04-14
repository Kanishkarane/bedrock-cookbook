"""
Specialized extractors for SEC filings
"""

import boto3
import json
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

REGION = "us-east-1"
MODEL_ID = "us.amazon.nova-pro-v1:0"


@dataclass
class ExtractionResult:
    """Result of an extraction operation."""
    data: dict
    source_text: str
    success: bool
    error: str = None
    
    def to_dict(self):
        return {
            "data": self.data,
            "success": self.success,
            "error": self.error
        }


class SECExtractor:
    """
    Extract structured data from SEC filings.
    """
    
    def __init__(self):
        self.client = boto3.client("bedrock-runtime", region_name=REGION)
    
    def _call_amazon(self, prompt: str) -> str:
        """Make a call to Amazon Nova Pro."""
        body = json.dumps({
            "messages": [{"role": "user", 
                          "content": [{"text":prompt}]}]
        })
        
        response = self.client.invoke_model(modelId=MODEL_ID, body=body)
        response_body = json.loads(response["body"].read())
        return response_body["output"]["message"]["content"][0]["text"]
    
    def _parse_json(self, text: str) -> dict:
        """Parse JSON from Amazon Nova Pro's response."""
        # Clean up response
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        return json.loads(text)
    
    def extract_financials(self, text: str) -> ExtractionResult:
        """
        Extract financial metrics from SEC filing text.
        """
        prompt = f"""Extract financial metrics from this SEC filing text. Return JSON only.

<schema>
{{
  "revenue": {{
    "amount_billions": number or null,
    "year": number,
    "yoy_change_percent": number or null
  }},
  "operating_income": {{
    "amount_billions": number or null,
    "year": number
  }},
  "net_income": {{
    "amount_billions": number or null,
    "year": number
  }},
  "segments": [
    {{
      "name": string,
      "revenue_billions": number or null
    }}
  ]
}}
</schema>

<instructions>
- Extract exact numbers from the text
- Convert all amounts to billions USD
- Include year-over-year changes if mentioned
- List major business segments if mentioned
- Use null for values not found in the text
</instructions>

<text>
{text}
</text>

Return ONLY the JSON object, no explanation."""

        try:
            response = self._call_amazon(prompt)
            data = self._parse_json(response)
            return ExtractionResult(data=data, source_text=text, success=True)
        except Exception as e:
            return ExtractionResult(data={}, source_text=text, success=False, error=str(e))
    
    def extract_risks(self, text: str) -> ExtractionResult:
        """
        Extract risk factors from SEC filing text.
        """
        prompt = f"""Extract risk factors from this SEC filing text. Return JSON only.

<schema>
{{
  "risks": [
    {{
      "category": string,
      "title": string,
      "summary": string (1-2 sentences max)
    }}
  ],
  "total_risks_mentioned": number
}}
</schema>

<instructions>
- Identify distinct risk factors
- Categorize each risk (e.g., "Operational", "Financial", "Regulatory", "Competitive", "Macroeconomic")
- Keep summaries brief and factual
- List up to 10 most significant risks
</instructions>

<text>
{text}
</text>

Return ONLY the JSON object, no explanation."""

        try:
            response = self._call_amazon(prompt)
            data = self._parse_json(response)
            return ExtractionResult(data=data, source_text=text, success=True)
        except Exception as e:
            return ExtractionResult(data={}, source_text=text, success=False, error=str(e))
    
    def extract_executives(self, text: str) -> ExtractionResult:
        """
        Extract executive information from SEC filing text.
        """
        prompt = f"""Extract executive/leadership information from this SEC filing text. Return JSON only.

<schema>
{{
  "executives": [
    {{
      "name": string,
      "title": string,
      "age": number or null,
      "tenure_years": number or null
    }}
  ],
  "board_size": number or null
}}
</schema>

<instructions>
- Extract names and titles of executives mentioned
- Include age if stated
- Include tenure/years at company if mentioned
- Include board of directors count if mentioned
</instructions>

<text>
{text}
</text>

Return ONLY the JSON object, no explanation."""

        try:
            response = self._call_amazon(prompt)
            data = self._parse_json(response)
            return ExtractionResult(data=data, source_text=text, success=True)
        except Exception as e:
            return ExtractionResult(data={}, source_text=text, success=False, error=str(e))


# Test with chunks from your indexed documents
if __name__ == "__main__":
    import sys
    sys.path.append("../01-document-qa")
    from retriever import Retriever
    
    retriever = Retriever()
    extractor = SECExtractor()
    
    print("="*60)
    print("FINANCIAL EXTRACTION TEST")
    print("="*60)
    
    # Get chunks about revenue
    chunks = retriever.retrieve("Amazon revenue net sales financial results", k=3)
    combined_text = "\n\n".join([c.text for c in chunks])
    
    result = extractor.extract_financials(combined_text)
    print("\nExtracted financials:")
    print(json.dumps(result.data, indent=2))
    
    print("\n" + "="*60)
    print("RISK EXTRACTION TEST")
    print("="*60)
    
    # Get chunks about risks
    chunks = retriever.retrieve("risk factors challenges threats", k=3)
    combined_text = "\n\n".join([c.text for c in chunks])
    
    result = extractor.extract_risks(combined_text)
    print("\nExtracted risks:")
    print(json.dumps(result.data, indent=2))
    
    print("\n" + "="*60)
    print("EXECUTIVE EXTRACTION TEST")
    print("="*60)
    
    # Get chunks about leadership
    chunks = retriever.retrieve("CEO executives officers leadership management", k=3)
    combined_text = "\n\n".join([c.text for c in chunks])
    
    result = extractor.extract_executives(combined_text)
    print("\nExtracted executives:")
    print(json.dumps(result.data, indent=2))