"""
Download SEC 10-K filings for Amazon
"""

import requests
import os
from pathlib import Path

# SEC EDGAR API headers (required)
HEADERS = {
    "User-Agent": "Kanishka bedrock-cookbook@example.com"  # Replace with your email
}

# Amazon's CIK (Central Index Key)
AMAZON_CIK = "0001018724"

# Output directory
OUTPUT_DIR = Path("data/raw")


def get_10k_filings(cik: str, count: int = 3) -> list:
    """
    Get recent 10-K filing URLs for a company.
    """
    # SEC API endpoint
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    
    filings = []
    recent = data["filings"]["recent"]
    
    for i, form in enumerate(recent["form"]):
        if form == "10-K" and len(filings) < count:
            accession = recent["accessionNumber"][i].replace("-", "")
            primary_doc = recent["primaryDocument"][i]
            filing_date = recent["filingDate"][i]
            
            file_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_doc}"
            filings.append({
                "date": filing_date,
                "url": file_url,
                "accession": accession
            })
    
    return filings


def download_filing(filing: dict, output_dir: Path) -> str:
    """
    Download a single filing.
    """
    response = requests.get(filing["url"], headers=HEADERS)
    response.raise_for_status()
    
    filename = f"AMZN_10K_{filing['date']}.htm"
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    return str(filepath)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Fetching Amazon 10-K filing information...")
    filings = get_10k_filings(AMAZON_CIK, count=3)
    
    print(f"Found {len(filings)} filings\n")
    
    for filing in filings:
        print(f"Downloading {filing['date']} filing...")
        filepath = download_filing(filing, OUTPUT_DIR)
        print(f"  ✓ Saved to {filepath}")
    
    print("\nDone!")