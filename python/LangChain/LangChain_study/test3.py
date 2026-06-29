import os

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

search_tool = TavilySearchResults(max_results=3)
query = "LangChain 是什么"

search_result = search_tool.invoke({"query": query})

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个信息整理助手，请基于搜索结果给出简洁、准确的中文总结。"),
        ("human", "问题：{query}\n\n搜索结果：\n{search_result}"),
    ]
)

chain = prompt | llm
response = chain.invoke(
    {
        "query": query,
        "search_result": str(search_result),
    }
)

print("Tavily 搜索结果：")
print(search_result)
print()
print("DeepSeek 总结：")
print(response.content)
