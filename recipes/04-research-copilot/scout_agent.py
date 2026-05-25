import arxiv
import requests

from typing import TypedDict, List, Annotated

from langchain.tools import tool
from langchain_aws import ChatBedrock

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver



# LLM

llm = ChatBedrock(
    model_id="amazon.nova-pro-v1:0"
)


# TOOLS
CACHE = {}
@tool
def search_arxiv(query: str):
    """Search arXiv for academic papers."""

    if query in CACHE:
        print("Using cache...")
        return CACHE[query]

    client = arxiv.Client()

    search = arxiv.Search(
        query=query,
        max_results=3,
        sort_by=arxiv.SortCriterion.Relevance
    )

    papers = []

    for result in client.results(search):

        papers.append({
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "published": str(result.published),
            "abstract": result.summary,
            "url": result.pdf_url
        })
    CACHE[query]=papers
    return papers


@tool
def search_semantic_scholar(query: str):
    """Search Semantic Scholar for academic papers."""

    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    params = {
        "query": query,
        "limit": 3,
        "fields": "title,authors,abstract,url,year,citationCount"
    }

    response = requests.get(url, params=params)

    data = response.json()

    papers = []

    for p in data.get("data", []):

        papers.append({
            "title": p.get("title"),
            "authors": [a["name"] for a in p.get("authors", [])],
            "abstract": p.get("abstract"),
            "url": p.get("url"),
            "year": p.get("year"),
            "citations": p.get("citationCount")
        })

    return papers


# BIND TOOLS

tools = [search_arxiv, search_semantic_scholar]

llm_with_tools = llm.bind_tools(tools)


# STATE

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]
    papers: List[dict]
    query: str



# AGENT NODE

def scout_agent(state: ResearchState):

    response = llm_with_tools.invoke(state["messages"])

    return {
        "messages": [response]
    }



# TOOL NODE


tool_node = ToolNode(tools)


# SUMMARIZER NODE

def summarize(state: ResearchState):

    all_papers = []

    for msg in state["messages"]:

        if hasattr(msg, "content"):
            try:
                content=eval(msg.content)

                if isinstance(content,list):
                    all_papers.extend(content)
            except:
                pass
    unique_papers = deduplicate_papers(all_papers)
    ranked_papers = rank_papers(unique_papers)
    ranked_papers = ranked_papers[:5]


    prompt = f"""
    Summarize these research findings clearly:

    {ranked_papers}

    Mention:
    - main ideas
    - trends
    - important papers
    """

    response = llm.invoke(prompt)

    return {
        "messages": [response]
    }


# ROUTER

def router(state: ResearchState):

    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "summarize"


# BUILD GRAPH

graph = StateGraph(ResearchState)

graph.add_node("agent", scout_agent)
graph.add_node("tools", tool_node)
graph.add_node("summarize", summarize)

graph.add_edge(START, "agent")

graph.add_conditional_edges(
    "agent",
    router,
    {
        "tools": "tools",
        "summarize": "summarize"
    }
)

graph.add_edge("tools", "agent")

graph.add_edge("summarize", END)


# MEMORY

memory = InMemorySaver()


# COMPILE

app = graph.compile(checkpointer=memory)



def deduplicate_papers(papers):

    seen=set()
    unique_papers=[]

    for paper in papers:
        title=paper.get("title","").lower().strip()

        if title not in seen:
            seen.add(title)
            unique_papers.append(paper)

    return unique_papers


def rank_papers(papers):

    return sorted(
        papers,
        key=lambda x: x.get("citations", 0),
        reverse=True
    )


def main():

    print("=" * 50)
    print("Research Copilot - Scout Agent")
    print("Type 'quit' to exit")
    print("=" * 50)

    config = {
        "configurable": {
            "thread_id": "user-1"
        }
    }

    while True:

        query = input("\nYou: ").strip()

        if query.lower() == "quit":
            print("Goodbye!")
            break

        result = app.invoke(
            {
                "messages": [("user", query)],
                "papers": [],
                "query": query
            },
            config=config
        )

        print("\nScout Agent:\n")

        print(result["messages"][-1].content)

if __name__ == "__main__":
    main()