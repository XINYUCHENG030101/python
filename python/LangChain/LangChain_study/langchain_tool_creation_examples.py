import os
from typing import Any, Type

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import BaseTool, StructuredTool, Tool, tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


# 方式 1：使用 @tool 装饰器创建最简单的工具。
@tool
def multiply(a: int, b: int) -> int:
    """计算两个整数的乘积。"""
    return a * b


# 方式 2：使用 @tool + args_schema 显式定义入参结构。
class WeatherInput(BaseModel):
    city: str = Field(..., description="要查询的城市")
    unit: str = Field(default="摄氏度", description="温度单位")


@tool(args_schema=WeatherInput)
def get_weather(city: str, unit: str = "摄氏度") -> str:
    """返回模拟天气结果。"""
    return f"{city} 今天晴天，温度 25 {unit}"


# 方式 3：使用 StructuredTool.from_function 创建结构化工具。
def add_numbers(a: int, b: int) -> int:
    """计算两个整数的和。"""
    return a + b


structured_add = StructuredTool.from_function(
    func=add_numbers,
    name="structured_add",
    description="计算两个整数的和。",
)


# 方式 4：使用 Tool.from_function 创建字符串输入的简单工具。
def search_docs(query: str) -> str:
    """模拟文档检索。"""
    return f"已为你检索关键字：{query}"


search_tool = Tool.from_function(
    func=search_docs,
    name="search_docs",
    description="根据关键词检索文档。",
)


# 方式 5：继承 BaseTool，自定义一个工具类。
class EchoInput(BaseModel):
    text: str = Field(..., description="要回显的文本")


class EchoTool(BaseTool):
    name: str = "echo_text"
    description: str = "把输入文本原样返回。"
    args_schema: Type[BaseModel] = EchoInput

    def _run(self, text: str) -> str:
        return f"回显结果：{text}"


echo_tool = EchoTool()


# 方式 6：把 Runnable 包装成工具。
class SummaryInput(BaseModel):
    topic: str = Field(..., description="摘要主题")
    count: int = Field(..., description="摘要条数")


def summarize_payload(payload: dict) -> str:
    return f"主题：{payload['topic']}，共生成 {payload['count']} 条摘要。"


runnable_tool = RunnableLambda(summarize_payload).as_tool(
    args_schema=SummaryInput,
    name="payload_summary",
    description="根据主题和数量生成摘要说明。",
)


def build_agent() -> Any:
    tools = [multiply, get_weather, structured_add, search_tool, echo_tool, runnable_tool]

    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        temperature=0,
    )

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt="你是一个会调用工具的助手。需要计算、检索或查询天气时优先使用工具。",
    )


if __name__ == "__main__":
    print("方式1 @tool：", multiply.invoke({"a": 3, "b": 4}))
    print("方式2 @tool + args_schema：", get_weather.invoke({"city": "北京", "unit": "摄氏度"}))
    print("方式3 StructuredTool.from_function：", structured_add.invoke({"a": 5, "b": 7}))
    print("方式4 Tool.from_function：", search_tool.invoke("LangChain tool"))
    print("方式5 继承 BaseTool：", echo_tool.invoke({"text": "你好"}))
    print("方式6 Runnable.as_tool：", runnable_tool.invoke({"topic": "LangChain", "count": 3}))

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("未检测到 DEEPSEEK_API_KEY，跳过 agent 示例。")
    else:
        agent_app = build_agent()
        agent_result = agent_app.invoke(
            {"messages": [HumanMessage(content="请先用 structured_add 计算 8 加 9，再告诉我北京天气，最后把结果整理成一句话。")]}
        )
        print("Agent 输出：", agent_result["messages"][-1].content)
