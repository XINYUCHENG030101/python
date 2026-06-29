from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class State(TypedDict):
    age: int | None


def get_age_node(state: State):
    """循环获取用户年龄，直到准确"""

    prompt = "请输入年龄："
    while True:
        age = interrupt(prompt)
        # 验证
        if isinstance(age, int) and age > 0:
            return {"age": age}
        # 更新错误提示
        prompt = f"请输入一个有效的年龄。需要大于0岁，且是一个整数"

builder = StateGraph(State)
builder.add_node(get_age_node)
builder.add_edge(START, "get_age_node")
builder.add_edge("get_age_node", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "1"}}
result1 = graph.invoke({}, config=config)
print(result1["__interrupt__"][0].value)

result2 = graph.invoke(Command(resume="三十"), config=config)
print(result2["__interrupt__"][0].value)

result3 = graph.invoke(Command(resume=18), config=config)
print(result3)



