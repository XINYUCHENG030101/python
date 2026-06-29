# test3.py Tavily + DeepSeek Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `LangChain_study/test3.py` 改成先调用 Tavily 搜索，再使用 DeepSeek 对搜索结果进行总结。

**Architecture:** 保留 `ChatOpenAI` 作为 DeepSeek 聊天模型，新增一个 Tavily 搜索调用步骤。先拿到 Tavily 返回结果，再把结果格式化成提示词交给模型总结，最后打印结构化搜索结果和总结文本。

**Tech Stack:** Python, LangChain, langchain-openai, langchain-community, Tavily

---

### Task 1: 重写 `test3.py`

**Files:**
- Modify: `e:\python\LangChain\LangChain_study\test3.py`

- [ ] **Step 1: 保留 DeepSeek 模型初始化并补充提示模板相关导入**

```python
import os

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
```

- [ ] **Step 2: 创建 Tavily 搜索工具并执行一次搜索**

```python
search_tool = TavilySearchResults(max_results=3)
search_result = search_tool.invoke({"query": "LangChain 是什么"})
```

- [ ] **Step 3: 用提示模板把搜索结果交给 DeepSeek 总结**

```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个信息整理助手，请基于搜索结果给出简洁、准确的中文总结。"),
        ("human", "问题：{query}\n\n搜索结果：\n{search_result}"),
    ]
)

chain = prompt | llm
response = chain.invoke(
    {
        "query": "LangChain 是什么",
        "search_result": str(search_result),
    }
)
```

- [ ] **Step 4: 打印原始搜索结果和模型总结**

```python
print("Tavily 搜索结果：")
print(search_result)
print()
print("DeepSeek 总结：")
print(response.content)
```

- [ ] **Step 5: 检查诊断，运行脚本前确认环境变量**

Run: `py -3.8 .\LangChain_study\test3.py`
Expected: 成功打印 Tavily 搜索结果以及 DeepSeek 中文总结
