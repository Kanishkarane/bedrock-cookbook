"""
Test SEC tools before giving them to the agent
"""

from sec_tools import (
    search_sec_filings, 
    extract_financials,
    extract_risks,
    extract_executives
)

print("="*60)
print("TEST 1: Search SEC Filings")
print("="*60)
result = search_sec_filings("AWS revenue growth", num_results=2)
print(result[:500])

print("\n" + "="*60)
print("TEST 2: Extract Financials")
print("="*60)
result = extract_financials("revenue and operating income 2022")
print(result)

print("\n" + "="*60)
print("TEST 3: Extract Risks")
print("="*60)
result = extract_risks("competition")
print(result)

print("\n" + "="*60)
print("TEST 4: Extract Executives")
print("="*60)
result = extract_executives()
print(result)