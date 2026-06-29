from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI


# 案例: 参数
examples = [
    {"text": "hi, what is your name?", "output": "你好，你叫什么名字？"},
    {"text": "hi, what is your age?", "output": "你好，你多大了？"},
]

# 与案例关联的聊天消息模板
examples_prompt_template = ChatPromptTemplate(
    [
        ("user", "{text}"),
        ("ai", "{output}"),
    ]
)

# 将案例转换为 消息列表，插入到提示词模板中去？
# 少样本提示词模板 (Runnable 实例)
few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,                         # 案例（参数）
    example_prompt=examples_prompt_template,   # ChatPromptTemplate 模板
)

# [
#       HumanMessage(content='hi, what is your name?', additional_kwargs={}, response_metadata={}),
#       AIMessage(content='你好，你叫什么名字？', additional_kwargs={}, response_metadata={}),
#       HumanMessage(content='hi, what is your age?', additional_kwargs={}, response_metadata={}),
#       AIMessage(content='你好，你多大了？', additional_kwargs={}, response_metadata={})
# ]
print(few_shot_prompt.invoke({}).to_messages())

# 最终提示词模板
chat_prompt_template = ChatPromptTemplate(
    [
        ("system", "将文本从{language_from}翻译为{language_to}"),
        # 示例
        few_shot_prompt,
        ("user", "{text}"),
    ]
)

# messages=[
#   SystemMessage(content='将文本从英文翻译为中文', additional_kwargs={}, response_metadata={}),
#   HumanMessage(content='hi, what is your name?', additional_kwargs={}, response_metadata={}),
#   AIMessage(content='你好，你叫什么名字？', additional_kwargs={}, response_metadata={}),
#   HumanMessage(content='hi, what is your age?', additional_kwargs={}, response_metadata={}),
#   AIMessage(content='你好，你多大了？', additional_kwargs={}, response_metadata={}),
#   HumanMessage(content='hi, what is your favourite food?', additional_kwargs={}, response_metadata={})
# ]
# print(chat_prompt_template.invoke(
#     {
#         "language_from": "英文",
#         "language_to": "中文",
#         "text": "hi, what is your favourite food?",
#     }
# ))

model = ChatOpenAI(model="gpt-4o-mini")
chain = chat_prompt_template | model
chain.invoke(
    {
        "language_from": "英文",
        "language_to": "中文",
        "text": "hi, what is your favourite food?",
    }
).pretty_print()

