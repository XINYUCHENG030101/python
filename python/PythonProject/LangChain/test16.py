from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")

# model.invoke("我是小明，你好！").pretty_print()
# model.invoke("你知道我是谁吗？").pretty_print()

# messages = [
#     HumanMessage(content="我是小明，你好！"),
#     AIMessage(content="你好，小明！很高兴认识你！今天有什么想聊的呢？"),
#     HumanMessage(content="你知道我是谁吗？"),
# ]
# model.invoke(messages).pretty_print()

store = {}
# 根据会话 id 查询会话里的消息列表
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        # InMemoryChatMessageHistory() 帮助我们将AIMessage、HumanMessage等消息自动添加进来
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 包装了 model, 让model具备存储历史消息的能力
with_history_message_model = RunnableWithMessageHistory(model, get_session_history)

# model: Runnable 实例
# invoke: config: 配置 Runnable 实例
config={"configurable": {"session_id" : "1"}}

with_history_message_model.invoke(
    [HumanMessage(content="我是小明，你好！")],
    config = config,
).pretty_print()

with_history_message_model.invoke(
    [HumanMessage(content="你知道我是谁吗？")],
    config = config,
).pretty_print()







