from typing import Any


import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence  # 新增：显式使用 RunnableSequence 定义链
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model


llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "请帮我翻译，由英文转换为中文"),
        ("human", "{text}"),
    ]
)

parser = StrOutputParser()

# 新增：使用 RunnableSequence 按顺序组合 prompt、llm 和 parser
chain = RunnableSequence[Any, Any](prompt, llm, parser)

resp = chain.invoke({"text": "hello"})
print(resp)
