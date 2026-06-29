from typing import Optional, List, TypedDict, Union

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing_extensions import Annotated

model = ChatOpenAI(model="gpt-4o-mini")

# Pydantic 对象
class Joke(BaseModel):
    """给用户讲的一个笑话"""

    setup: str = Field(description="这个笑话的开头")
    punchline: str = Field(description="这个笑话的妙语")
    rating: Optional[int] = Field(default=None, description="从1-10分，给这个笑话评分")


class Response(BaseModel):
    """用以对话的方式回应。"""

    content: str = Field(description="用于对用户查询的会话响应")

class FinalResponse(BaseModel):
    """最终回复，选择合适的输出结构"""

    final_output: Union[Joke, Response]

model_with_structured = model.with_structured_output(FinalResponse)
print(model_with_structured.invoke("讲一个关于跳舞的笑话"))
print(model_with_structured.invoke("你是谁？"))
