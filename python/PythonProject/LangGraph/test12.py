from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph


def node(state: MessagesState):
    model = init_chat_model("gpt-4o-mini")
    return {
        "messages": model.invoke(state["messages"])
    }

builder = StateGraph(MessagesState)
builder.add_node(node)
builder.add_edge(START, "node")
builder.add_edge("node", END)

graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "1"}}
graph.invoke({
    "messages": [HumanMessage(content="我叫小明")]
}, config=config)

graph.invoke({
    "messages": [HumanMessage(content="我是谁")]
}, config=config)["messages"][-1].pretty_print()

config2 = {"configurable": {"thread_id": "2"}}
graph.invoke({
    "messages": [HumanMessage(content="我是谁")]
}, config=config2)["messages"][-1].pretty_print()