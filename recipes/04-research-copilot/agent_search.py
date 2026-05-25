from langchain_aws import ChatBedrock
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode,tools_condition
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


llm = ChatBedrock(
    model_id='amazon.nova-pro-v1:0'
)
"""response = llm.invoke("What is Langgraph?")
print(response.content)"""

search_tool=DuckDuckGoSearchRun()
llm_with_tools=llm.bind_tools([search_tool])
'''result=search_tool.invoke("transformers papers published in 2024")
response=llm_with_tools.invoke("What papers were published about transformers in 2024?")
print(response)
print(response.tool_calls)'''

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

graph=graph_builder.compile()

result = graph.invoke({
    "messages": [
        (
        "user",
        "What papers were published about transformers in 2024?"
        )
    ]
})

for m in result["messages"]:
    print(m)
    print()