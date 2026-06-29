from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")

class State(TypedDict):
    query: str
    summary: str
    translation: str


def generate_summary(state: State):
    """生成摘要"""
    response = model.invoke([
        {"role": "user", "content": f"请为以下内容生成摘要：{state['query']}"}
    ])

    # response = model.invoke([
    #     {"role": "user", "content": f"请为以下内容进行润色：{state['query']}，超过100字"}
    # ])
    return {"summary": response.content}


def generate_translation(state: State):
    """生成翻译"""
    response = model.invoke([
        {"role": "user", "content": f"请将以下内容翻译成英文：{state['query']}"}
    ])
    return {"translation": response.content}


# 构建并行处理图
builder = StateGraph(State)
builder.add_node("summarize", generate_summary)
builder.add_node("translate", generate_translation)

builder.add_edge(START, "summarize")
builder.add_edge(START, "translate")
builder.add_edge("summarize", END)
builder.add_edge("translate", END)
graph = builder.compile()

# 流式输出并只显示某个节点的 Tokens
target_node = "summarize"  # 可以改为 "translate"
for token_chunk, metadata in graph.stream(
        {"query": "人工智能是计算机科学的一个分支，致力于创造能够执行通常需要人类智能的任务的机器。"},
        stream_mode="messages"
):
    # print(metadata)
    # if token_chunk.content:
    #     print(token_chunk.content, end="", flush=True)
    # 根据元数据中的node进行过滤打印
    node_name = metadata.get("langgraph_node", "")
    if token_chunk.content and node_name == "summarize":  # 先打印总结输出
        print(token_chunk.content, end="", flush=True)