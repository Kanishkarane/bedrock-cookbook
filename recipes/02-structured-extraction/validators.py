"""
Validation helpers for extracted data
"""

from typing import Optional


def validate_financials(data: dict) -> dict:
    """
    Validate and clean financial extraction results.
    
    Returns dict with 'valid' boolean and 'issues' list.
    """
    issues = []
    
    # Check revenue
    if "revenue" in data:
        rev = data["revenue"]
        if rev.get("amount_billions") is not None:
            if rev["amount_billions"] < 0:
                issues.append("Revenue cannot be negative")
            if rev["amount_billions"] > 10000:
                issues.append("Revenue seems unreasonably high (>$10T)")
    
    # Check operating income
    if "operating_income" in data:
        oi = data["operating_income"]
        if oi.get("amount_billions") is not None:
            rev_amt = data.get("revenue", {}).get("amount_billions")
            if rev_amt and abs(oi["amount_billions"]) > rev_amt:
                issues.append("Operating income exceeds revenue")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


def validate_executives(data: dict) -> dict:
    """
    Validate executive extraction results.
    """
    issues = []
    
    if "executives" in data:
        for exec in data["executives"]:
            if not exec.get("name"):
                issues.append("Executive missing name")
            if not exec.get("title"):
                issues.append(f"Executive {exec.get('name', 'unknown')} missing title")
            if exec.get("age") and (exec["age"] < 18 or exec["age"] > 100):
                issues.append(f"Executive {exec.get('name')} has unlikely age: {exec['age']}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


def validate_risks(data: dict) -> dict:
    """
    Validate risk extraction results.
    """
    issues = []
    
    if "risks" in data:
        for risk in data["risks"]:
            if not risk.get("title"):
                issues.append("Risk missing title")
            if not risk.get("category"):
                issues.append(f"Risk '{risk.get('title', 'unknown')}' missing category")
            if risk.get("summary") and len(risk["summary"]) > 500:
                issues.append(f"Risk summary too long: {risk.get('title')}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }