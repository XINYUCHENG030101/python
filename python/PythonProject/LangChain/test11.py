from langchain_openai import ChatOpenAI
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage

# 定义大模型
model = ChatOpenAI(model="gpt-4o-mini")

class Person(BaseModel):
    """一个人的信息。"""

    # 注意:
    # 1. 每个字段都是 Optional “可选的” —— 允许 LLM 在不知道答案时输出 None。
    # 2. 每个字段都有一个 description “描述” —— LLM使用这个描述。
    # 有一个好的描述可以帮助提高提取结果。
    name: Optional[str] = Field(default=None, description="这个人的名字")
    hair_color: Optional[str] = Field(default=None, description="如果知道这个人头发的颜色")
    skin_color: Optional[str] = Field(default=None, description="如果知道这个人的肤色")
    height_in_meters: Optional[str] = Field(default=None, description="以米为单位的高度")


structured_model = model.with_structured_output(schema=Person)
messages = [
    SystemMessage(content="你是一个提取信息的专家，只从文本中提取相关信息。如果您不知道要提取的属性的值，属性值返回null"),
    HumanMessage(content="史密斯身高6英尺，金发。")
]
result = structured_model.invoke(messages)
print(result)