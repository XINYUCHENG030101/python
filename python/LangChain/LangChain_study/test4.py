import os

from langchain.chat_models import init_chat_model
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage, ToolMessage


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"请先设置环境变量: {name}")
    return value


llm = init_chat_model(
    "deepseek-chat",
    model_provider="openai",
    api_key=require_env("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

search_tool = TavilySearchResults(max_results=3)
llm_with_tools = llm.bind_tools([search_tool])

query = "LangChain 是什么？请结合最新公开资料做一个简洁中文总结。"
messages = [HumanMessage(content=query)]

first_response = llm_with_tools.invoke(messages)
messages.append(first_response)

print("第一次模型响应：")
print(first_response.content or "[模型返回了工具调用请求，文本内容为空]")
print()

if not first_response.tool_calls:
    print("模型这次没有触发工具调用。")
else:
    print("模型请求的工具调用：")
    print(first_response.tool_calls)
    print()

    for tool_call in first_response.tool_calls:
        if tool_call["name"] != search_tool.name:
            raise ValueError(f"未识别的工具名称: {tool_call['name']}")

        tool_result = search_tool.invoke(tool_call["args"])
        messages.append(
            ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
        )

    final_response = llm_with_tools.invoke(messages)

    print("最终回答：")
    print(final_response.content)
