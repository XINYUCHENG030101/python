from langchain.chat_models import init_chat_model
from langchain_core.messages import trim_messages, RemoveMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.types import Overwrite

model = init_chat_model("gpt-4o-mini")

# 场景二：管理调用LLM时的消息列表
# def call_model(state: MessagesState):
#     """调用LLM"""
#     # 调用 LLM 时的消息裁剪
#     messages = trim_messages(
#         state["messages"],
#         strategy="last",     # 策略：保留最后部分
#         token_counter=model, # 计算token数
#         max_tokens=128,       # 最大token数
#         start_on="human",    # 从用户消息开始裁剪
#         end_on=("human", "tool"), # 结束于..
#     )
#     result = model.invoke(messages)
#     return {"messages": [result]}

# 场景二：管理状态中的消息列表
# def call_model(state: MessagesState):
#     """调用LLM"""
#
#     # # 清空State中的消息
#     # return {"messages": Overwrite([])}
#
#     # 根据消息id删除state中的指定消息:RemoveMessage对象，通过return删除
#     # RemoveMessage 只能删除带有add_messages的消息：messages: Annotated[list[AnyMessage], add_messages]
#     # return {"messages": [RemoveMessage(id=state["messages"][2].id)]}
#     if len(state["messages"]) > 5:
#         return {"messages": [RemoveMessage(id=msg.id) for msg in state["messages"][:5]]}
#
#     result = model.invoke(state["messages"])
#     return {"messages": [result]}

# def call_model(state: MessagesState):
#     """调用LLM"""
#
#     # 删除所有消息
#     return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)]}

class State(MessagesState):
    summary: str   # 总结

def call_model(state: State):
    """调用LLM"""
    summary = state.get("summary", "")
    # 小结消息+被裁剪过的消息
    return {"messages": [model.invoke([HumanMessage(content=summary)] + state["messages"])]}

def summarize_conversation(state: State):
    """生成历史总结"""

    # 1. 生成历史总结
    summary = state.get("summary", "")
    if summary:
        # 已存在摘要总结，需要重写摘要总结
        summary_message = (
            f"这是到目前为止的对话摘要：{summary}\n"
            "基于上面的新消息扩展摘要："
        )
    else:
        # 不存在摘要总结，需要新增摘要总结
        summary_message = "创建上述对话的摘要"

    result = model.invoke(state["messages"] + [HumanMessage(content=summary_message)])

    # 2. 删除state中的历史消息（每次对话都删除一次）

    return {
        "summary": result.content,
        "messages": [RemoveMessage(id=m.id) for m in state["messages"][:-1]] # 只保留最后一个消息（目的为了打印消息结果）
    }

builder = StateGraph(State)
builder.add_node(call_model)
builder.add_node(summarize_conversation)

builder.add_edge(START, "call_model")
builder.add_edge("call_model", "summarize_conversation")
builder.add_edge("summarize_conversation", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "1"}}
result1 = graph.invoke({"messages": "hi, my name is bob"}, config)
print(result1["summary"])
result1["messages"][-1].pretty_print()
# H，A
result2 = graph.invoke({"messages": "write a short poem about cats"}, config)
print(result2["summary"])
result2["messages"][-1].pretty_print()

# H，A，H，A
result3 = graph.invoke({"messages": "now do the same but for dogs"}, config)
print(result3["summary"])
result3["messages"][-1].pretty_print()

# for msg in result["messages"]:
#     msg.pretty_print()
    # H，A，H，A, H, A
final_response = graph.invoke({"messages": "你知道我是谁吗"}, config)
# H，A，H，A, H, A，H
print(final_response["summary"])

for msg in final_response["messages"]:
    msg.pretty_print()
