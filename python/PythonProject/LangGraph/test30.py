from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph


# 子图
class SubState(TypedDict):
    sub: str      # sub 私有
    parent: str   # 可以和父状态共享   # 父状态写入

def sub_node_1(state: SubState):
    return {"sub": "pass sub node 1"}

def sub_node_2(state: SubState):
    return {"parent": state["parent"] + state["sub"]}

sub_builder = StateGraph(SubState)
sub_builder.add_sequence([sub_node_1, sub_node_2])
sub_builder.add_edge(START, "sub_node_1")
sub_graph = sub_builder.compile()

# print(sub_graph.invoke({"parent": "hahahah"}))

# 主图(没有调用子图)
class State(TypedDict):
    parent: str    # 输入和输入

def node_1(state: State):
    return {"parent": "hi, " + state["parent"]}


builder = StateGraph(State)
builder.add_node(node_1)
builder.add_node("sub_node", sub_graph)   # 关键：直接将编译好的子图添加进主图节点
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "sub_node")
builder.add_edge("sub_node", END)
# 如果图包含子图，则只需要在编译主图时设置检查点。LangGraph 会自动将检查点传播到子图
graph = builder.compile(checkpointer=InMemorySaver())
# print(graph.invoke({"parent": "小明"}))
for chunk in graph.stream({"parent": "小明"}, subgraphs=True):
    print(chunk)





