from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class State(TypedDict):
    input: str
    output: str


def node(state: State):
    """进行中断操作"""

    # 中断恢复后，从调用interrupt的节点开始重新执行
    # 因此对于interrupt前的代码，需要幂等
    print("1111111111111111111111111")
    # 中断
    result = interrupt("结束还是继续？yes表示继续，no表示结束")
    if result == "yes":
        return {
            "output": "你好，我是你的贴心助手！"
        }
    else:
        return {
            "output": "人工结束工作流"
        }

builder = StateGraph(State)
builder.add_node(node)
builder.add_edge(START, "node")
builder.add_edge("node", END)
# 重要：编译图，必须带上checkpoint！
graph = builder.compile(checkpointer=InMemorySaver())

# 外部
config = {"configurable": {"thread_id": "1"}}
result1 = graph.invoke({"input": "hi"}, config=config)
print(result1["__interrupt__"][0].value)

# 恢复：将Command对象发送给图
result2 = graph.invoke(Command(resume="yes"), config=config)
print(result2)

# 将来恢复工作流的时候，可以用resume参数将信息带回工作流
# Command(resume="no")