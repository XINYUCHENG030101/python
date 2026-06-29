from typing import Optional, List, TypedDict

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing_extensions import Annotated

model = ChatOpenAI(model="gpt-4o-mini")

# Pydantic 对象
# class Joke(BaseModel):
#     """给用户讲的一个笑话"""
#
#     setup: str = Field(description="这个笑话的开头")
#     punchline: str = Field(description="这个笑话的妙语")
#     rating: Optional[int] = Field(default=None, description="从1-10分，给这个笑话评分")
#
# class Data(BaseModel):
#     """获取关于笑话的数据列表"""
#
#     jokes: List[Joke]

# TypedDict
# class Joke(TypedDict):
#     """给用户讲的一个笑话"""
#
#     setup: Annotated[str, ..., "这个笑话的开头"]
#     punchline: Annotated[str, ..., "这个笑话的妙语"]
#     rating: Annotated[Optional[int], None, "从1-10分，给这个笑话评分"]
#
#
# # model_with_structured = model.with_structured_output(Joke)
# # print(model_with_structured.invoke("讲一个关于跳舞的笑话"))
# model_with_structured = model.with_structured_output(Joke, include_raw=True)
# print(model_with_structured.invoke("讲一个关于跳舞的笑话"))


# JSON Schema
json_schema = {
    "title": "joke",
    "description": "给用户讲一个笑话。",
    "type": "object",
    "properties": {
        "setup": {
            "type": "string",
            "description": "这个笑话的开头",
        },
        "punchline": {
            "type": "string",
            "description": "这个笑话的妙语",
        },
        "rating": {
            "type": "integer",
            "description": "从1到10分，给这个笑话评分",
            "default": None,
        },
    },
    "required": ["setup", "punchline"],
}

model_with_structured = model.with_structured_output(json_schema)
# print(model_with_structured.invoke("讲一个关于跳舞的笑话"))
print(model_with_structured.invoke("你是谁？"))


# print(model.invoke("讲一个关于唱歌的笑话").content)