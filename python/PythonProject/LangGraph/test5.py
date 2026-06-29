from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph


class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str

class State(InputState, OutputState):
    pass

def node(state: InputState):
    """通过问题生成答案"""

    return {
        "question": state["question"],
        "answer": f"Answer to: {state["question"]}"
    }

builder = StateGraph(
    State,
    input_schema=InputState,    # 输入验证
    output_schema=OutputState)  # 输出过滤
builder.add_node(node)
builder.add_edge(START, "node")
builder.add_edge("node", END)

graph = builder.compile()
result = graph.invoke({
    "question": "i am a question"
})
print(result)
# 按照StateGraph(State)创建的图，执行后返回 State
# 希望得到的结果只有 answer

