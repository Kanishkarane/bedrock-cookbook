from typing import TypedDict 
from langgraph.graph import StateGraph,START,END

class State(TypedDict):
    messages:list[str]

def greeter(state:State):
    return {
        "messages": state["messages"]+["Hello from Greeter!"]
    }

def responder(state:State):
    return {
        "messages": state["messages"]+["Hello from Responder!"]
    }

graph = StateGraph(State)
graph.add_node("greeter",greeter)
graph.add_node("responder",responder)
graph.add_edge(START,"greeter")
graph.add_edge("greeter","responder")
graph.add_edge("responder",END)
app = graph.compile()

result = app.invoke({
    "messages":[]
})
print(result)
