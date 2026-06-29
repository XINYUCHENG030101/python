from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class State(TypedDict):
    text: str

def review_node(state: State):
    """通过中断，让审查者编辑生成的内容"""

    updated = interrupt({
        "instruction": "查看并编辑内容",
        "content": state["text"]
    })

    if updated["success"] == "true":
        return {}
    else:
        return {
            "text": updated["content"]
        }

builder = StateGraph(State)
builder.add_node(review_node)
builder.add_edge(START, "review_node")
builder.add_edge("review_node", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "1"}}
result1 = graph.invoke({"text": "初始文章...."}, config=config)
print(result1["__interrupt__"])

# .... 审核中 ....

print(graph.invoke(Command(resume={"success": "false", "content": "编辑后的文章..."}), config=config))


