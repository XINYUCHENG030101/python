from typing import TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph

# 公共状态
class State(TypedDict):
    result: str

class Node1OutputState(TypedDict):
    # 隐私数据
    sensitive_data: str

class Node2InputState(TypedDict):
    # 隐私数据
    sensitive_data: str

def node_1(state: State) -> Node1OutputState:
    """第一步：获取隐私数据"""
    print("node1：获取隐私数据")
    return {
        "sensitive_data": "我是隐私数据"
    }

def node_2(state: Node2InputState) -> State:
    """第二步：拿到隐私数据，去处理（生成非隐私数据）"""
    print("node2：拿到隐私数据，去处理")
    return {
        "result": "处理后的数据"
    }

def node_3(state: State):
    """第三步：构造返回结果"""
    print("node3：构造返回结果")
    return {
        "result": state["result"] + "- 完成"
    }

builder = StateGraph(State)
# 添加了3个节点，并规定好了执行顺序
builder.add_sequence([node_1, node_2, node_3])
builder.add_edge(START, "node_1")
# node_3 不指向 END
graph = builder.compile()
print(graph.invoke({
    "result": ""
}))