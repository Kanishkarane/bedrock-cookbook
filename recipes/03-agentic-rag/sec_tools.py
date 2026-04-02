"""
SEC Filing tools for the agent
"""

import json
import sys
from strands import tool

# Add path to existing recipes
sys.path.append("../01-document-qa")
sys.path.append("../02-structured-extraction")

from retriever import Retriever
from extractors import SECExtractor


# Initialize once (reused across tool calls)
_retriever = None
_extractor = None


def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def get_extractor():
    global _extractor
    if _extractor is None:
        _extractor = SECExtractor()
    return _extractor


@tool
def search_sec_filings(query: str, num_results: int = 5) -> str:
    """
    Search Amazon's SEC 10-K filings for relevant information.
    
    Use this tool when you need to find specific information from 
    Amazon's annual reports, such as financial data, business 
    descriptions, risk factors, or strategic initiatives.
    
    Args:
        query: What to search for (e.g., "AWS revenue growth", "risk factors")
        num_results: Number of relevant passages to return (default: 5)
    
    Returns:
        Relevant passages from SEC filings with source information
    """
    retriever = get_retriever()
    chunks = retriever.retrieve(query, k=num_results)
    
    if not chunks:
        return "No relevant information found in SEC filings."
    
    results = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.file.split("/")[-1].replace(".htm", "")
        results.append(f"[Source {i}: {source}]\n{chunk.text[:500]}...")
    
    return "\n\n---\n\n".join(results)


@tool
def extract_financials(query: str) -> str:
    """
    Extract structured financial data from Amazon's SEC filings.
    
    Use this tool when you need specific financial metrics in a 
    structured format, such as revenue, operating income, or 
    segment breakdowns.
    
    Args:
        query: What financial data to find (e.g., "revenue and operating income")
    
    Returns:
        JSON with structured financial data
    """
    retriever = get_retriever()
    extractor = get_extractor()
    
    # First retrieve relevant context
    chunks = retriever.retrieve(f"Amazon {query} financial results earnings", k=5)
    context = "\n\n".join([c.text for c in chunks])
    
    # Then extract structured data
    result = extractor.extract_financials(context)
    
    if result.success:
        return json.dumps(result.data, indent=2)
    else:
        return f"Extraction failed: {result.error}"


@tool
def extract_risks(query: str = "risk factors") -> str:
    """
    Extract risk factors from Amazon's SEC filings.
    
    Use this tool when you need to understand what risks Amazon 
    faces, categorized and summarized.
    
    Args:
        query: Optional specific risk area to focus on
    
    Returns:
        JSON with categorized risk factors
    """
    retriever = get_retriever()
    extractor = get_extractor()
    
    # Retrieve risk-related context
    chunks = retriever.retrieve(f"Amazon {query} challenges threats", k=5)
    context = "\n\n".join([c.text for c in chunks])
    
    # Extract structured risks
    result = extractor.extract_risks(context)
    
    if result.success:
        return json.dumps(result.data, indent=2)
    else:
        return f"Extraction failed: {result.error}"


@tool
def extract_executives() -> str:
    """
    Extract executive and leadership information from Amazon's SEC filings.
    
    Use this tool when you need information about Amazon's 
    leadership team, executives, or board of directors.
    
    Returns:
        JSON with executive names, titles, and other details
    """
    retriever = get_retriever()
    extractor = get_extractor()
    
    # Retrieve leadership context
    chunks = retriever.retrieve("Amazon CEO executives officers leadership management board", k=5)
    context = "\n\n".join([c.text for c in chunks])
    
    # Extract structured data
    result = extractor.extract_executives(context)
    
    if result.success:
        return json.dumps(result.data, indent=2)
    else:
        return f"Extraction failed: {result.error}"


# List of all tools for easy import
ALL_TOOLS = [
    search_sec_filings,
    extract_financials,
    extract_risks,
    extract_executives,
]