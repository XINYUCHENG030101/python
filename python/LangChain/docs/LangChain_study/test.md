# test.py 逐句讲解

## 脚本作用

`test.py` 是这一组示例里最基础的一篇。它的核心目的是演示：

- 如何创建一个聊天模型对象
- 如何定义一个消息模板
- 如何把 Prompt、模型和输出解析器组合成一条最基础的 Runnable 链

如果你只想先理解 LangChain 最小可运行链路，这个脚本应该是起点。

## 运行前提

- 已安装 `langchain`
- 已安装 `langchain-core`
- 已安装 `langchain-openai`
- 已设置环境变量 `DEEPSEEK_API_KEY`

## 完整代码

```python
from typing import Any


import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence  # 新增：显式使用 RunnableSequence 定义链
from langchain_openai import ChatOpenAI
from langchain.chat_models import init_chat_model


llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "请帮我翻译，由英文转换为中文"),
        ("human", "{text}"),
    ]
)

parser = StrOutputParser()

# 新增：使用 RunnableSequence 按顺序组合 prompt、llm 和 parser
chain = RunnableSequence[Any, Any](prompt, llm, parser)

resp = chain.invoke({"text": "hello"})
print(resp)
```

## 分段讲解

### 导入区

- `from typing import Any` 导入类型标注里的 `Any`。它表示“这里可以是任意类型”。
- `import os` 用于读取环境变量。
- `StrOutputParser` 是输出解析器，用来把模型输出整理成普通字符串。
- `ChatPromptTemplate` 是聊天提示模板类。
- `RunnableSequence` 是 LangChain 用来显式拼接多个 Runnable 的类。
- `ChatOpenAI` 是聊天模型适配器。
- `init_chat_model` 在这个脚本里并没有真正被使用，因此你可以把它视为一个多余导入；这也提醒我们阅读脚本时要区分“被导入”与“被使用”。

### 模型初始化区

```python
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
```

- `llm` 是一个变量名，通常代表大语言模型对象。
- `model="deepseek-chat"` 指定要调用的 DeepSeek 模型名称。
- `api_key=os.getenv("DEEPSEEK_API_KEY")` 从系统环境变量中读取 API Key。
- `base_url="https://api.deepseek.com"` 指定兼容接口地址。

### Prompt 定义区

```python
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "请帮我翻译，由英文转换为中文"),
        ("human", "{text}"),
    ]
)
```

- `from_messages(...)` 用来根据消息列表构造聊天模板。
- `"system"` 消息用于定义任务边界，这里要求模型做英译中翻译。
- `"human"` 消息表示用户输入。
- `"{text}"` 是模板变量，不是 Python f-string，而是 Prompt 模板自己的占位语法。

### 解析器与链组合区

```python
parser = StrOutputParser()
chain = RunnableSequence[Any, Any](prompt, llm, parser)
```

- `parser = StrOutputParser()` 创建输出解析器对象。
- `RunnableSequence[Any, Any](prompt, llm, parser)` 的重点不是方括号里的 `Any, Any`，而是它把 3 个 Runnable 串起来：
  - `prompt` 先把变量填到模板里
  - `llm` 再去调用模型
  - `parser` 最后提取文本输出
- 这里的 `Any, Any` 只是类型提示，不改变运行时行为。

### 执行区

```python
resp = chain.invoke({"text": "hello"})
print(resp)
```

- `invoke(...)` 是同步调用入口。
- 传入的字典里有一个键 `text`，正好对应前面 Prompt 中的 `{text}`。
- `print(resp)` 会打印最终翻译结果。

## 执行流程

脚本先创建聊天模型对象，再创建一个用于翻译的提示模板，然后创建字符串输出解析器。接着用 `RunnableSequence` 把三者串起来，最后把 `"hello"` 填进模板并执行整条链，打印出中文翻译结果。

## 关键对象与机制

- `ChatOpenAI`：负责真正和 DeepSeek 兼容接口通信。
- `ChatPromptTemplate`：负责构造结构化消息。
- `StrOutputParser`：把模型消息对象转成普通字符串。
- `RunnableSequence`：显式串联多个 Runnable。

## 容易踩坑点

- 环境变量 `DEEPSEEK_API_KEY` 缺失时会导致模型调用失败。
- `RunnableSequence` 的类型参数容易让初学者误以为它会改变运行时逻辑，实际上这里只是类型提示。
- `init_chat_model` 这个导入没有被实际使用，阅读时不要误以为它参与了执行链。

## 可扩展方向

- 把 `RunnableSequence` 改写成 `prompt | llm | parser`，对比两种写法。
- 把翻译任务改成摘要、改写或问答任务。
- 在 Prompt 中增加更多消息角色，体验多消息模板的组织方式。
