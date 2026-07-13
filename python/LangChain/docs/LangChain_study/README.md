# LangChain_study 学习文档

## 学习地图

`LangChain_study` 目录里的 8 个脚本覆盖了模型调用、Prompt 组合、运行时配置、工具定义、Agent、搜索工具和工具调用消息流等主题。这套文档的目标不是只告诉你“代码能跑”，而是帮助你从 Python 语法、LangChain 机制和第三方库 API 三个层面逐段理解这些脚本。

如果你刚开始学 LangChain，可以把这组示例理解成一条由浅入深的学习链路：

- 先理解最基础的 `prompt + llm + parser`
- 再理解模型对象如何被运行时配置覆盖
- 接着理解工具是如何定义和暴露给模型的
- 最后理解搜索工具、工具绑定和消息流中的工具调用协议

## 推荐学习顺序

建议按照下面顺序阅读：

1. `test.py`
2. `chat_model_all_params.py`
3. `test2.py`
4. `openai_to_deepseek_configurable.py`
5. `openai_to_deepseek_with_prefix.py`
6. `langchain_tool_creation_examples.py`
7. `test3.py`
8. `test4.py`

这个顺序从最基础的 Runnable 串联开始，逐步进入可配置模型、工具定义、Agent 和手动工具调用。

## 脚本索引

- [test.md](file:///e:/github/python/LangChain/docs/LangChain_study/test.md)：最基础的 Prompt、模型和输出解析器串联。
- [chat_model_all_params.md](file:///e:/github/python/LangChain/docs/LangChain_study/chat_model_all_params.md)：聚焦 `ChatOpenAI` 初始化参数和 Runnable 管道写法。
- [test2.md](file:///e:/github/python/LangChain/docs/LangChain_study/test2.md)：最简版 `init_chat_model()` 动态配置示例。
- [openai_to_deepseek_configurable.md](file:///e:/github/python/LangChain/docs/LangChain_study/openai_to_deepseek_configurable.md)：演示如何用 `init_chat_model()` 暴露运行时可切换字段。
- [openai_to_deepseek_with_prefix.md](file:///e:/github/python/LangChain/docs/LangChain_study/openai_to_deepseek_with_prefix.md)：演示多个模型实例如何用配置前缀隔离运行时参数。
- [langchain_tool_creation_examples.md](file:///e:/github/python/LangChain/docs/LangChain_study/langchain_tool_creation_examples.md)：演示 6 种工具定义方式，以及新版 `create_agent()` 的用法。
- [test3.md](file:///e:/github/python/LangChain/docs/LangChain_study/test3.md)：直接调用 Tavily 搜索，再把结果交给模型总结。
- [test4.md](file:///e:/github/python/LangChain/docs/LangChain_study/test4.md)：让模型触发工具调用，并手工把工具结果接回消息流。

## 核心概念总览

- `ChatOpenAI`：LangChain 中统一的聊天模型适配器。虽然名字里有 `OpenAI`，但只要服务提供 OpenAI 兼容接口，也可以接到 DeepSeek 这类模型服务。
- `init_chat_model()`：LangChain 提供的模型初始化辅助函数，适合演示运行时可覆盖字段和多模型配置。
- `ChatPromptTemplate`：把系统消息、人类消息等结构化地组织成模型输入，而不是手写一个大字符串。
- `StrOutputParser`：把模型输出从消息对象中抽成普通字符串，便于继续处理或直接打印。
- `Runnable`：LangChain 对“可执行组件”的统一抽象，`prompt | llm | parser` 和 `RunnableSequence(...)` 本质上都在组合 Runnable。
- `tool` / `StructuredTool` / `BaseTool`：LangChain 暴露工具能力的几种典型方式，适合不同复杂度的工具定义场景。
- `create_agent()`：当前版本中构建 Agent 的主入口，它会把模型、工具和消息流拼成一个可执行图。
- `bind_tools()`：告诉模型“你可以调用这些工具”，常用于手工控制消息流的工具调用示例。
- `ToolMessage`：把真实工具执行结果重新送回模型时所使用的消息类型，用于维持工具调用链条的上下文一致性。

## 每篇文档怎么看

这组文档统一使用类似的讲解框架：

- `脚本作用`：先说清楚这个脚本在整条学习链路里负责什么主题。
- `运行前提`：说明依赖包、环境变量和联网要求。
- `完整代码`：贴出和源码一致的代码，方便你一边对照一边读。
- `分段讲解`：按导入区、模型初始化区、工具区、调用区等自然结构拆开说明。
- `执行流程`：把从上到下的运行顺序串起来。
- `关键对象与机制`：单独解释最值得学习的 LangChain 组件。
- `容易踩坑点`：提醒版本差异、环境变量和接口兼容问题。
- `可扩展方向`：告诉你这个示例下一步可以怎么改。

## 读这组文档前的准备

为了顺利理解并运行这些脚本，建议先具备以下前置知识：

- 知道 Python 中 `import`、函数、类、类型注解、字典和列表这些基础语法
- 知道环境变量是什么，以及 `os.getenv()` 的作用
- 了解大模型调用的基本概念，例如模型名、温度、最大输出长度

如果你对 LangChain 还很陌生，也没关系。独立文档会尽量在解释具体语句时同时补上对应的概念背景。
