"""
Configuration management - handles local .env and Streamlit Cloud secrets
"""

import os

def get_config():
    """
    Get configuration from environment or Streamlit secrets.
    """
    try:
        # Try Streamlit secrets first (for cloud deployment)
        import streamlit as st
        return {
            "aws_access_key_id": st.secrets["AWS_ACCESS_KEY_ID"],
            "aws_secret_access_key": st.secrets["AWS_SECRET_ACCESS_KEY"],
            "aws_region": st.secrets.get("AWS_DEFAULT_REGION", "us-east-1"),
            "opensearch_endpoint": st.secrets["OPENSEARCH_ENDPOINT"],
        }
    except:
        # Fall back to environment variables (for local development)
        from dotenv import load_dotenv
        load_dotenv()
        return {
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "aws_region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            "collection_endpoint": os.getenv("COLLECTION_ENDPOINT"),
        }