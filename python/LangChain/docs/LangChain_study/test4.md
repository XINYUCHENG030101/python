# test4.py 逐句讲解

## 脚本作用

`test4.py` 展示的是比 `test3.py` 更深入的一层：不是程序先固定执行搜索，再把结果交给模型，而是先把工具绑定给模型，让模型自己决定要不要调用工具。程序再根据模型返回的 `tool_calls` 去执行真实工具，并把工具结果以 `ToolMessage` 的形式送回模型。

这个脚本非常适合理解 LangChain 和聊天模型中的“工具调用消息流”。

## 运行前提

- 已安装 `langchain`
- 已安装 `langchain-community`
- 已设置环境变量 `DEEPSEEK_API_KEY`
- 已设置环境变量 `TAVILY_API_KEY`
- 当前网络可以访问 Tavily 与 DeepSeek 服务

## 完整代码

```python
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
```

## 分段讲解

### 导入区

- `init_chat_model` 用来创建聊天模型对象。
- `TavilySearchResults` 是搜索工具。
- `HumanMessage` 和 `ToolMessage` 是 LangChain 消息体系中的两种消息类型：
  - `HumanMessage` 表示用户消息
  - `ToolMessage` 表示工具返回结果消息

### 环境变量检查函数

```python
def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"请先设置环境变量: {name}")
    return value
```

- `def require_env(...)` 定义了一个辅助函数，用来强制要求某个环境变量必须存在。
- `name: str` 表示参数是字符串。
- `-> str` 表示函数成功时会返回字符串。
- `if not value:` 是 Python 的真假判断写法。空字符串和 `None` 都会被当作假值。
- `raise ValueError(...)` 主动抛出异常，比让底层请求阶段再报错更早、更清晰。

### 模型与工具绑定区

```python
llm = init_chat_model(
    "deepseek-chat",
    model_provider="openai",
    api_key=require_env("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

search_tool = TavilySearchResults(max_results=3)
llm_with_tools = llm.bind_tools([search_tool])
```

- `require_env("DEEPSEEK_API_KEY")` 确保环境变量缺失时立即失败。
- `search_tool` 是实际要给模型使用的工具。
- `llm.bind_tools([search_tool])` 可以理解成“把这个工具能力注册给模型”。
- 绑定之后，模型在生成消息时可以返回 `tool_calls`，告诉程序“我想调用哪个工具、参数是什么”。

### 初始化消息流

```python
query = "LangChain 是什么？请结合最新公开资料做一个简洁中文总结。"
messages = [HumanMessage(content=query)]
```

- `messages` 是一个列表，里面放的是消息对象，而不是纯字符串。
- 这里把用户问题显式包装成 `HumanMessage`，这是因为当前脚本要在消息流层面手工控制工具调用过程。

### 第一次模型调用

```python
first_response = llm_with_tools.invoke(messages)
messages.append(first_response)
```

- 第一次调用时，模型会看到用户问题和可用工具列表。
- 模型可能直接给出答案，也可能决定先发起工具调用。
- `messages.append(first_response)` 很重要，因为后续消息流必须保留模型第一轮的响应，无论它是普通文本还是工具调用请求。

### 判断是否触发工具调用

```python
if not first_response.tool_calls:
    print("模型这次没有触发工具调用。")
else:
    ...
```

- `first_response.tool_calls` 是一个很关键的字段。
- 如果它为空，说明模型这次没有请求工具。
- 如果它不为空，说明模型已经返回了一个或多个工具调用请求。

### 执行工具并回填消息流

```python
for tool_call in first_response.tool_calls:
    if tool_call["name"] != search_tool.name:
        raise ValueError(f"未识别的工具名称: {tool_call['name']}")

    tool_result = search_tool.invoke(tool_call["args"])
    messages.append(
        ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
    )
```

- `for tool_call in first_response.tool_calls` 遍历模型提出的每个工具调用请求。
- `tool_call["name"]` 是模型要求调用的工具名。
- 先做一次工具名检查，是为了避免程序去执行未预期的工具。
- `search_tool.invoke(tool_call["args"])` 说明模型给出的参数会被直接拿去执行真实工具。
- `ToolMessage(...)` 是这里最关键的机制之一：
  - `content=str(tool_result)`：把工具结果转成文本内容
  - `tool_call_id=tool_call["id"]`：把结果和模型先前发出的那次工具调用请求对应起来
- 如果没有正确的 `tool_call_id`，模型在下一轮通常无法知道这条工具结果是回应哪一次请求的。

### 第二次模型调用

```python
final_response = llm_with_tools.invoke(messages)
```

- 这时 `messages` 里已经有：
  - 用户消息
  - 模型第一轮响应
  - 工具结果消息
- 因此模型可以基于完整上下文生成最终回答。

## 执行流程

脚本先检查环境变量，然后创建聊天模型对象与搜索工具，并把工具绑定给模型。接着脚本构造用户消息列表，发起第一次模型调用。如果模型没有请求工具，脚本就直接结束说明；如果模型请求了工具，程序会遍历这些工具请求，执行真实搜索，把结果包装成 `ToolMessage` 加回消息列表，最后再次调用模型生成最终回答。

## 关键对象与机制

- `bind_tools()`：把工具能力注册给模型。
- `HumanMessage`：用户在消息流中的表示形式。
- `tool_calls`：模型请求工具时返回的结构化字段。
- `ToolMessage`：把工具执行结果反馈给模型的标准消息类型。
- 两阶段调用：先看模型要不要工具，再执行工具，再把结果回传。

## 容易踩坑点

- 如果不追加 `first_response`，后续消息流就会缺失“模型曾经请求过工具”这一事实。
- 如果 `ToolMessage` 没有正确的 `tool_call_id`，模型通常无法把工具结果与原请求对应起来。
- 这类脚本对消息顺序非常敏感，顺序错了就可能让模型理解上下文失败。
- 和 `test3.py` 相比，这里更接近 Agent 内部机制，但代码也更容易写错。

## 可扩展方向

- 绑定多个工具，观察模型如何在多工具之间选择。
- 把这段手工消息流逻辑封装成通用函数。
- 和 `create_agent()` 版本对照阅读，理解“手工消息流控制”和“Agent 封装”之间的关系。
