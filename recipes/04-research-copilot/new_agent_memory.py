from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_aws import ChatBedrock
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode,tools_condition
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

memory=SqliteSaver.from_conn_string("research_memory.db")
llm = ChatBedrock(
    model_id='amazon.nova-pro-v1:0'
)
search_tool=DuckDuckGoSearchRun()
llm_with_tools=llm.bind_tools([search_tool])

class state(TypedDict):
    messages:Annotated[list[AnyMessage],add_messages]

def agent(State:state):
    response=llm_with_tools.invoke(State["messages"])

    return {
        "messages":[response]
    }
tool_node=ToolNode([search_tool])

graph_builder=StateGraph(state)

graph_builder.add_node("agent",agent)
graph_builder.add_node("tools",tool_node)

graph_builder.add_edge(START,"agent")
graph_builder.add_conditional_edges("agent",tools_condition)
graph_builder.add_edge("tools","agent")

with SqliteSaver.from_conn_string("research_memory.db") as memory:

    graph=graph_builder.compile(checkpointer=memory)

    config={
        "configurable":{
            "thread_id":"user-123"
        }
    }

    result = graph.invoke({
        "messages": [
            (
            "user",
            "What is my favourite topic?"
            )
        ]
        },
        config = config
    )

for m in result["messages"]:
    print(m)
    print()