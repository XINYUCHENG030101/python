from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


model = ChatOpenAI(model="gpt-4o-mini")

# 定义文本提示词模板, Runnable 实例
# 方式1：
# prompt_template = PromptTemplate(
#     template="介绍{city}的历史",
#     input_variables=["city"],
# )

# # 方式2
# prompt_template = PromptTemplate.from_template("将文本从{language_from}翻译为{language_to}")
#
# # 调用：实例化模板
# print(prompt_template.invoke({"language_from": "英文", "language_to": "中文"}))

# 处理聊天消息的模板
# chat_prompt_template = ChatPromptTemplate(
#     [
#         ("system", "将文本从{language_from}翻译为{language_to}"),
#         ("user", "{text}"),
#         # ("ai", "")
#     ]
# )
# 实例化
# messages=[
#   SystemMessage(content='将文本从英文翻译为中文', additional_kwargs={}, response_metadata={}),
#   HumanMessage(content='hi, what is your name?', additional_kwargs={}, response_metadata={})
# ]
# messages = chat_prompt_template.invoke(
#     {
#         "language_from": "英文",
#         "language_to": "中文",
#         "text": "hi, what is your name?"
#     }
# )
# # print(messages)
# model.invoke(messages).pretty_print()


chat_prompt_template = ChatPromptTemplate(
    [
        ("system", "将文本从{language_from}翻译为{language_to}"),
        MessagesPlaceholder("msgs"),  # 消息占位符
        ("user", "{text}"),
        # ("ai", "")
    ]
)

messages_placeholder = [
    HumanMessage(content="hi, what is your name?"),
    AIMessage(content="你好，你叫什么名字？")
]

messages = chat_prompt_template.invoke(
    {
        "language_from": "英文",
        "language_to": "中文",
        "text": "hi, what is your age?",
        "msgs": messages_placeholder,
    }
)
print(messages)

# chain = chat_prompt_template | model
# chain.invoke(
#     {
#         "language_from": "英文",
#         "language_to": "中文",
#         "text": "hi, what is your age?",
#         "msgs": messages_placeholder,
#     }
# ).pretty_print()


