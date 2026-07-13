# langchain_tool_creation_examples.py 逐句讲解

## 脚本作用

这个脚本是整组示例里信息量最大的一篇。它一口气展示了：

- 6 种定义 LangChain 工具的方法
- `pydantic` 在工具参数约束中的作用
- `BaseTool` 自定义类写法
- `RunnableLambda.as_tool()` 的包装方式
- 新版 `create_agent()` 如何把模型和工具拼成 Agent

如果你想理解“LangChain 为什么能让模型调用工具”，这个脚本就是关键入口。

## 运行前提

- 已安装 `langchain`
- 已安装 `langchain-core`
- 已安装 `langchain-openai`
- 已安装 `pydantic`
- 已设置环境变量 `DEEPSEEK_API_KEY`

## 完整代码

```python
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
```

## 分段讲解

### 导入区

- `from typing import Any, Type` 里的 `Any` 表示“任意类型”，`Type[...]` 表示“某个类对象的类型”。
- `from langchain.agents import create_agent` 导入新版 Agent 构造入口。当前项目使用的 LangChain 版本已经不是旧版 `AgentExecutor` 主导的写法。
- `HumanMessage` 是 LangChain 的消息对象类型之一，用来表示用户消息。
- `RunnableLambda` 允许你把普通 Python 可调用对象包装成 Runnable。
- `BaseTool`、`StructuredTool`、`Tool`、`tool` 分别对应不同复杂度的工具定义方式。
- `BaseModel` 和 `Field` 来自 `pydantic`，它们不仅用于类型提示，还会在运行时承担参数校验和元数据描述的职责。

### 方式 1：`@tool` 装饰器

```python
@tool
def multiply(a: int, b: int) -> int:
    """计算两个整数的乘积。"""
    return a * b
```

- `@tool` 是 Python 装饰器语法。它会在函数定义完成后，把函数包装成 LangChain 能识别的工具对象。
- `a: int` 和 `b: int` 是类型注解，告诉读者和工具系统这两个参数应该是整数。
- `-> int` 表示函数返回整数。
- 三引号 docstring 会被 LangChain 当作工具描述的一部分，因此不是“可有可无的注释”。
- `return a * b` 是最普通的 Python 返回语句，但一旦套上 `@tool`，这个返回值就会成为工具执行结果。

### 方式 2：`@tool + args_schema`

```python
class WeatherInput(BaseModel):
    city: str = Field(..., description="要查询的城市")
    unit: str = Field(default="摄氏度", description="温度单位")
```

- `class WeatherInput(BaseModel)` 定义了一个 `pydantic` 模型类。
- `city: str` 表示字段名为 `city`，类型是字符串。
- `Field(..., description="要查询的城市")` 中的 `...` 不是省略号装饰，而是一个特殊哨兵值，表示该字段必填。
- `default="摄氏度"` 表示 `unit` 字段有默认值，不传也可以。

```python
@tool(args_schema=WeatherInput)
def get_weather(city: str, unit: str = "摄氏度") -> str:
    """返回模拟天气结果。"""
    return f"{city} 今天晴天，温度 25 {unit}"
```

- 这里的 `args_schema=WeatherInput` 不是给 Python 类型系统看的，而是明确告诉 LangChain：这个工具的输入结构由 `WeatherInput` 负责描述和校验。
- `unit: str = "摄氏度"` 既是 Python 默认参数，也是工具的默认输入值。
- `f"{city} ... {unit}"` 是 Python f-string，用来把变量插入字符串中。

### 方式 3：`StructuredTool.from_function`

```python
structured_add = StructuredTool.from_function(
    func=add_numbers,
    name="structured_add",
    description="计算两个整数的和。",
)
```

- `StructuredTool.from_function(...)` 是类方法工厂模式，它会根据函数签名自动生成结构化工具。
- `func=add_numbers` 把前面定义的普通函数交给工具工厂。
- `name=` 和 `description=` 用于覆盖默认推断出来的名称和描述。
- 这种方式适合你已经有普通业务函数，只想快速把它转成 LangChain 工具。

### 方式 4：`Tool.from_function`

```python
search_tool = Tool.from_function(
    func=search_docs,
    name="search_docs",
    description="根据关键词检索文档。",
)
```

- `Tool` 相对更偏“简单字符串输入”的工具包装。
- 和 `StructuredTool` 对比，它更轻量，但结构化能力通常也更弱。
- 这里搭配的 `search_docs(query: str)` 很适合这种模式，因为它只接收一个字符串参数。

### 方式 5：继承 `BaseTool`

```python
class EchoTool(BaseTool):
    name: str = "echo_text"
    description: str = "把输入文本原样返回。"
    args_schema: Type[BaseModel] = EchoInput

    def _run(self, text: str) -> str:
        return f"回显结果：{text}"
```

- `class EchoTool(BaseTool)` 表示你开始手写一个工具类，而不是用工厂函数快捷生成。
- `name: str = "echo_text"` 和 `description: str = ...` 这里必须带类型注解，原因不仅是可读性，更是因为当前 `pydantic v2` 下类字段覆盖需要显式声明类型。
- `args_schema: Type[BaseModel] = EchoInput` 可以拆成三层理解：
  - Python 语法层面：这是一个类属性赋值。
  - 类型层面：它表示“这个属性应该是某个 `BaseModel` 子类本身”，而不是实例。
  - LangChain 机制层面：工具系统会读取这个 schema，知道该如何校验输入参数。
- `_run()` 是同步执行入口。对于 `BaseTool` 子类，LangChain 约定你至少要实现这个方法之一。

### 方式 6：把 Runnable 包装成工具

```python
runnable_tool = RunnableLambda(summarize_payload).as_tool(
    args_schema=SummaryInput,
    name="payload_summary",
    description="根据主题和数量生成摘要说明。",
)
```

- `RunnableLambda(summarize_payload)` 先把普通函数包装成 Runnable。
- `.as_tool(...)` 再把 Runnable 转成工具。
- 这种方式体现了 LangChain 的统一抽象思路：函数、Runnable、Tool 之间可以相互转换。
- 当前版本下 `as_tool()` 会有 beta 警告，但并不影响示例运行。

### Agent 构建区

```python
def build_agent() -> Any:
    tools = [multiply, get_weather, structured_add, search_tool, echo_tool, runnable_tool]
    ...
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt="你是一个会调用工具的助手。需要计算、检索或查询天气时优先使用工具。",
    )
```

- `tools = [...]` 是 Python 列表，把多个工具对象收集起来。
- `build_agent() -> Any` 返回 `Any`，说明这里没有再细抠返回图对象的精确类型，重点是可用性。
- `create_agent(...)` 是当前版本里创建 Agent 的主要入口。
- `model=llm` 表示 Agent 背后真正调用的模型。
- `tools=tools` 把可用工具注册给 Agent。
- `system_prompt=...` 是给 Agent 的系统级行为约束，不是普通用户输入。

### 主程序执行区

```python
if __name__ == "__main__":
```

- 这是 Python 的脚本入口判断。只有当前文件被“直接运行”时，下面代码才会执行；如果只是被别的文件导入，这一段不会跑。

```python
print("方式1 @tool：", multiply.invoke({"a": 3, "b": 4}))
```

- `invoke(...)` 是 LangChain 常见的统一调用接口。
- 注意这里传的是 `{"a": 3, "b": 4}`，因为该工具输入是结构化参数，不是单字符串。

```python
print("方式4 Tool.from_function：", search_tool.invoke("LangChain tool"))
```

- 这里直接传字符串，是因为这个工具更接近“单字符串输入”的用法。

```python
agent_result = agent_app.invoke(
    {"messages": [HumanMessage(content="请先用 structured_add 计算 8 加 9，再告诉我北京天气，最后把结果整理成一句话。")]}
)
```

- 当前版本 Agent 的输入核心是 `messages`，不是旧示例里常见的单一 `input` 字段。
- `HumanMessage(...)` 明确告诉系统：这是用户消息，而不是系统消息或工具消息。
- `agent_result["messages"][-1].content` 的意思是：取消息列表最后一条消息的文本内容，通常它就是 Agent 最终回答。

## 执行流程

脚本先定义 6 种工具，然后分别演示它们如何独立调用。之后脚本检查环境变量，如果找不到 `DEEPSEEK_API_KEY`，就只展示工具部分；如果找到了，就进一步构建 Agent，把这些工具交给模型使用。最后 Agent 会根据用户消息决定是否调用工具，并返回整理好的自然语言回答。

## 关键对象与机制

- `@tool`：最直接的工具声明方式。
- `BaseModel` / `Field`：工具输入结构和元数据的核心来源。
- `StructuredTool`：适合从普通函数快速生成结构化工具。
- `BaseTool`：适合需要完全自定义工具行为的场景。
- `RunnableLambda.as_tool()`：展示 Runnable 和 Tool 的统一抽象关系。
- `create_agent()`：把模型、工具和消息流组合起来的当前主入口。

## 容易踩坑点

- 旧版 `AgentExecutor` / `create_tool_calling_agent` 示例在当前项目版本中已经不适用。
- `langchain_core.pydantic_v1` 在当前环境不可用，要直接使用 `pydantic`。
- `BaseTool` 子类字段在 `pydantic v2` 下需要显式类型标注，否则容易报字段覆盖错误。
- 工具的 `invoke()` 传参形式取决于工具定义方式，不能一律传字符串，也不能一律传字典。

## 可扩展方向

- 把模拟天气工具改成真实 API 调用。
- 增加异步工具版本，对比 `_run()` 和 `_arun()`。
- 演示多个工具连续调用的更复杂 Agent 场景。
- 把工具输入输出改造成更严格的结构化数据。
