from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, trim_messages
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")

# 历史消息记录
messages = [
    SystemMessage(content="you're a good assistant"),
    HumanMessage(content="hi! I'm bob"),
    AIMessage(content="hi!"),
    HumanMessage(content="I like vanilla ice cream"),
    AIMessage(content="nice"),
    HumanMessage(content="whats 2 + 2"),
    AIMessage(content="4"),
    HumanMessage(content="thanks"),
    AIMessage(content="no problem!"),
    HumanMessage(content="having fun?"),
    AIMessage(content="yes!"),
    HumanMessage(content="What's my name?"),
]

# trim
# 使用 trim_messages 减少发送给模型的消息数量
# trimmer = trim_messages(
#     max_tokens=65,          # 修剪消息的最大令牌数，根据你想要的谈话长度来调整
#     strategy="last",        # 修剪策略：
#                             # “last”（默认）：保留最后的消息。
#                             # “first”：保留最早的消息。
#     token_counter=model,    # 传入一个函数或一个语言模型（因为语言模型有消息令牌计数方法）
#     include_system=True,    # 如果想始终保留初始系统消息，可以指定 include_system=True
#     allow_partial=False,    # 是否允许拆分消息的内容
#     start_on="human",       # 如果需要确保我们的第一条消息（不包括系统消息）始终是特定类型，可以指定 start_on
# )

trimmer = trim_messages(
    max_tokens=11,          # 修剪消息的最大令牌数，根据你想要的谈话长度来调整
    strategy="last",        # 修剪策略：
                            # “last”（默认）：保留最后的消息。
                            # “first”：保留最早的消息。
    token_counter=len,      # 传入一个函数或一个语言模型（因为语言模型有消息令牌计数方法）
    include_system=True,    # 如果想始终保留初始系统消息，可以指定 include_system=True
    allow_partial=False,    # 是否允许拆分消息的内容
    start_on="human",       # 如果需要确保我们的第一条消息（不包括系统消息）始终是特定类型，可以指定 start_on
)


chain = trimmer | model

# [SystemMessage(content="you're a good assistant", additional_kwargs={}, response_metadata={}),
# HumanMessage(content='I like vanilla ice cream', additional_kwargs={}, response_metadata={}),
# AIMessage(content='nice', additional_kwargs={}, response_metadata={}),
# HumanMessage(content='whats 2 + 2', additional_kwargs={}, response_metadata={}),
# AIMessage(content='4', additional_kwargs={}, response_metadata={}),
# HumanMessage(content='thanks', additional_kwargs={}, response_metadata={}),
# AIMessage(content='no problem!', additional_kwargs={}, response_metadata={}),
# HumanMessage(content='having fun?', additional_kwargs={}, response_metadata={}),
# AIMessage(content='yes!', additional_kwargs={}, response_metadata={}),
# HumanMessage(content="What's my name?", additional_kwargs={}, response_metadata={})]
# print(trimmer.invoke(messages))

print(chain.invoke(messages))
