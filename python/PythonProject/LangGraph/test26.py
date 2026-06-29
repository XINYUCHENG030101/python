from typing import TypedDict
from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI

# 定义状态
class State(TypedDict):
    input: str
    output: str

# 初始化模型
model = ChatOpenAI(model="gpt-4o-mini")
def llm_node(state: State):
    """生成答案的节点"""
    return {"output": model.invoke([
                {"role": "system", "content": "你是一个乐于助人的助手。"},
                {"role": "user", "content": state["input"]}
            ])
    }

# 构建图
builder = StateGraph(State)
builder.add_node(llm_node)
builder.add_edge(START, "llm_node")
graph = builder.compile()


# 流式输出 LLM Tokens
# 输出格式为(message_chunk, metadata) 元组。
for token_chunk, metadata in graph.stream(
        {"input": "请解释什么是机器学习？"},
        stream_mode="messages"
):
    # stream_mode="messages" 返回的内容与节点无关，只和model有关
    if token_chunk.content:
        print(token_chunk.content, end="", flush=True)