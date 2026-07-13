# test3.py 逐句讲解

## 脚本作用

`test3.py` 展示的是一种非常常见的 LLM 应用模式：先通过外部搜索工具拿到资料，再把资料交给模型做总结。你可以把它理解成最小版的“检索增强生成”思路。

在这个脚本里：

- Tavily 负责搜索
- DeepSeek 负责总结

## 运行前提

- 已安装 `langchain-community`
- 已安装 `langchain-openai`
- 已设置环境变量 `DEEPSEEK_API_KEY`
- 已设置环境变量 `TAVILY_API_KEY`
- 当前网络可以访问 Tavily 与 DeepSeek 服务

## 完整代码

```python
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
```

## 分段讲解

### 导入区

- `TavilySearchResults` 是 LangChain 社区包中的搜索工具封装。
- `ChatPromptTemplate` 用于把“问题”和“搜索结果”组织成结构化提示。
- `ChatOpenAI` 负责调用 DeepSeek 的兼容接口。

### 模型与搜索工具初始化区

```python
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

search_tool = TavilySearchResults(max_results=3)
query = "LangChain 是什么"
```

- `llm` 是模型对象。
- `search_tool = TavilySearchResults(max_results=3)` 创建一个搜索工具实例。
- `max_results=3` 表示最多返回 3 条搜索结果。
- `query = "LangChain 是什么"` 把查询词单独提出来存入变量，方便后面复用。

### 搜索执行区

```python
search_result = search_tool.invoke({"query": query})
```

- 这里调用的是工具对象的统一接口 `invoke(...)`。
- 传入的是 `{"query": query}` 这样的字典，而不是裸字符串，因为这个工具期待结构化输入。
- `search_result` 一般会是一个列表，里面包含标题、链接、摘要等信息。

### Prompt 组织区

```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个信息整理助手，请基于搜索结果给出简洁、准确的中文总结。"),
        ("human", "问题：{query}\n\n搜索结果：\n{search_result}"),
    ]
)
```

- 系统消息定义了模型的角色：信息整理助手。
- 用户消息中同时包含两个占位变量：`{query}` 和 `{search_result}`。
- `\n\n` 是换行符，用来让提示词结构更清晰。

### 链执行区

```python
chain = prompt | llm
response = chain.invoke(
    {
        "query": query,
        "search_result": str(search_result),
    }
)
```

- `prompt | llm` 组成的是一条两段式 Runnable 链。
- 这里没有接 `StrOutputParser`，所以返回值仍然是消息对象。
- `str(search_result)` 的作用是把搜索结果转换成字符串，便于插入 Prompt 模板。
- 这种做法简单直接，但也提醒你：如果搜索结果结构很复杂，未来也可以考虑先做更细的格式化。

### 输出区

- `print("Tavily 搜索结果：")` 先打印原始检索结果，帮助观察外部工具到底返回了什么。
- `print(response.content)` 再打印模型总结文本。

## 执行流程

脚本先创建 DeepSeek 模型对象和 Tavily 搜索工具对象，然后用 `query` 发起一次真实搜索，得到搜索结果列表。接着脚本把查询词和搜索结果一起填入 Prompt 模板，交给模型做中文总结。最后脚本先打印原始搜索结果，再打印模型总结内容。

## 关键对象与机制

- `TavilySearchResults`：负责从外部搜索服务拿到结果。
- `ChatPromptTemplate`：负责把“搜索结果 + 问题”组织成模型能理解的结构化输入。
- `prompt | llm`：最小版检索后总结链。
- `str(search_result)`：把结构化检索结果粗略转成可插入提示词的文本。

## 容易踩坑点

- 缺少 `TAVILY_API_KEY` 会导致搜索工具调用失败。
- 当前 `langchain_community.tools.tavily_search` 会出现弃用警告，这是版本提醒，不代表脚本立刻不可用。
- 直接 `str(search_result)` 虽然方便，但结果格式可能比较冗长；如果要做生产级应用，通常会先对结果做筛选和重组。
- 这里没有用输出解析器，所以返回值不是纯字符串，而是消息对象，要通过 `.content` 取文本。

## 可扩展方向

- 先筛选搜索结果中的标题和摘要，再交给模型总结。
- 改成多轮问题，让模型先总结再回答追问。
- 把这个模式扩展成真正的 RAG 工作流，例如引入本地文档检索。
