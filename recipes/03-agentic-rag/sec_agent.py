"""
SEC Filing Agent - Agentic RAG for Amazon financial analysis
"""

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from sec_tools import ALL_TOOLS


SYSTEM_PROMPT = """You are a financial analyst assistant specializing in Amazon's SEC filings.

You have access to tools that can:
1. Search Amazon's 10-K SEC filings for specific information
2. Extract structured financial data (revenue, income, segments)
3. Extract and categorize risk factors
4. Extract executive/leadership information

Guidelines:
- Use tools when you need specific data from the filings
- For simple factual questions, search first then answer
- For structured data requests, use the extract tools
- Always cite which filing year your information comes from when possible
- If you can't find information, say so clearly
- Be concise but accurate

You do NOT need to use tools for:
- General knowledge questions about Amazon
- Explaining financial concepts
- Calculations on data you've already retrieved"""


def create_agent(verbose: bool = False):
    """Create and return the SEC filing agent."""
    
    # Use conversation manager to maintain context
    conversation_manager = SlidingWindowConversationManager(
        window_size=10  # Remember last 10 turns
    )
    
    agent = Agent(
        model='amazon.nova-pro-v1:0',
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        conversation_manager=conversation_manager
    )
    
    return agent


def run_with_trace(agent, query: str):
    """Run agent and show tool usage."""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print("="*60)
    
    # The agent returns the response directly
    response = agent(query)
    
    print(f"\nResponse:\n{response}")
    return response


def main():
    """Interactive session with the agent."""
    print("="*60)
    print("AMAZON SEC FILING AGENT")
    print("="*60)
    print("Ask questions about Amazon's business, financials, or risks.")
    print("Commands: 'quit' to exit, 'clear' to reset conversation\n")
    
    agent = create_agent()
    
    while True:
        query = input("\nYou: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if query.lower() == 'clear':
            agent = create_agent()
            print("Conversation cleared.")
            continue
        
        if not query:
            continue
        
        print("\nAgent thinking...\n")
        response = agent(query)
        print(f"Agent: {response}")


if __name__ == "__main__":
    main()