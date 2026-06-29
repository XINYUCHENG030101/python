from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, filter_messages, merge_message_runs
from langchain_openai import ChatOpenAI

# 历史消息记录
# messages = [
#     SystemMessage("你是一个聊天助手", id="1"),
#     HumanMessage("示例输入", id="2"),
#     AIMessage("示例输出", id="3"),
#     HumanMessage("真实输入", id="4"),
#     AIMessage("真实输出", id="5"),
# ]

# 按照类型筛选
# print(filter_messages(include_types="human").invoke(messages))
# print(filter_messages(messages, include_types="human"))

# 按照id筛选
# print(filter_messages(messages, exclude_ids=["3"]))

# 按照id+类型筛选
# print(filter_messages(messages, exclude_ids=["3"], include_types=[HumanMessage, AIMessage]))

model = ChatOpenAI(model="gpt-4o-mini")

# 历史消息记录
messages = [
    SystemMessage("你是一个聊天助手。"),
    SystemMessage("你总是以笑话回应。"),
    HumanMessage("为什么要使用 LangChain?"),
    HumanMessage("为什么要使用 LangGraph?"),
    AIMessage("因为当你试图让你的代码更有条理时，LangGraph 会让你感到“节点”是个好主意！"),
    AIMessage("不过别担心，它不会“分散”你的注意力！"),
    HumanMessage("选择LangChain还是LangGraph?"),
]

# 方式1
merger_message = merge_message_runs(messages)
model.invoke(merger_message).pretty_print()

# 方式2
# chain = merger | model
# chain.invoke(messages).pretty_print()