from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field

# 定义模型
model = ChatOpenAI(model="gpt-4o-mini")

# 定义工具
tool = TavilySearch(max_results=4)

# 绑定工具
model_with_tools = model.bind_tools([tool])

# 定义消息列表
messages = [
    HumanMessage("北京今天的天气怎么样？")
]
ai_message = model_with_tools.invoke(messages)
messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    tool_message = tool.invoke(tool_call)
    messages.append(tool_message)

class SearchResult(BaseModel):
    """结构化搜索对象"""

    query: str = Field(description="搜索查询")
    findings: str = Field(description="查询结果摘要")

model_with_structured = model_with_tools.with_structured_output(SearchResult)
print(model_with_structured.invoke(messages))


