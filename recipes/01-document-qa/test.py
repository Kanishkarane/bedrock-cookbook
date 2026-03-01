# test_env.py
from dotenv import load_dotenv
import os

load_dotenv()

endpoint = os.getenv("OPENSEARCH_ENDPOINT")
print(f"Endpoint: {endpoint}")