"""
Hello Strands - Your first agent
"""

from strands import Agent

# Create a basic agent (uses Bedrock + Claude Sonnet 4 by default)
agent = Agent()

# Ask it something
response = agent("What is RAG in the context of AI applications? Keep it brief.")

print(response)