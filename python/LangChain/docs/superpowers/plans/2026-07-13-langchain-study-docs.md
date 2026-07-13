# LangChain Study Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `docs/LangChain_study/` 下生成 1 篇总览文档和 8 篇脚本精讲文档，并通过自动化校验保证文档文件与核心章节完整。

**Architecture:** 先用一个轻量的 `unittest` 校验脚本固定文档目录、文件名和必需章节，再分两批编写文档内容。第一批覆盖总览与 4 个核心示例脚本，第二批覆盖 4 个 `test*.py` 学习脚本，最后统一回归检查，确保文档和当前代码一致。

**Tech Stack:** Python, unittest, Markdown, LangChain existing example scripts

---

## File Structure

- Create: `e:\github\python\LangChain\docs\LangChain_study\README.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\chat_model_all_params.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\langchain_tool_creation_examples.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\openai_to_deepseek_configurable.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\openai_to_deepseek_with_prefix.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\test.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\test2.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\test3.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\test4.md`
- Create: `e:\github\python\LangChain\tests\test_langchain_study_docs.py`

### Task 1: 建立文档校验基线

**Files:**
- Create: `e:\github\python\LangChain\tests\test_langchain_study_docs.py`

- [ ] **Step 1: 写 README 存在性与章节结构的失败测试**

```python
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs" / "LangChain_study"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class LangChainStudyDocsTests(unittest.TestCase):
    def test_readme_exists_with_core_sections(self) -> None:
        readme = DOCS_DIR / "README.md"
        self.assertTrue(readme.exists(), f"missing file: {readme}")

        text = read_text(readme)
        required_sections = [
            "# LangChain_study 学习文档",
            "## 学习地图",
            "## 推荐学习顺序",
            "## 脚本索引",
            "## 核心概念总览",
        ]
        for section in required_sections:
            self.assertIn(section, text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试，确认它因为 README 尚不存在而失败**

Run: `python -m unittest e:\github\python\LangChain\tests\test_langchain_study_docs.py -v`
Expected: FAIL with `missing file: e:\github\python\LangChain\docs\LangChain_study\README.md`

- [ ] **Step 3: 提交测试基线**

```bash
git add e:\github\python\LangChain\tests\test_langchain_study_docs.py
git commit -m "test: add readme structure check for langchain study docs"
```

### Task 2: 编写总览文档 README

**Files:**
- Create: `e:\github\python\LangChain\docs\LangChain_study\README.md`
- Test: `e:\github\python\LangChain\tests\test_langchain_study_docs.py`

- [ ] **Step 1: 写出 README 的最小实现内容**

```markdown
# LangChain_study 学习文档

## 学习地图

`LangChain_study` 目录里的 8 个脚本覆盖了模型调用、Prompt 组合、运行时配置、工具定义、Agent、搜索工具和工具调用消息流等主题。这套文档的目标不是只告诉你“代码能跑”，而是帮助你从 Python 语法、LangChain 机制和第三方库 API 三个层面逐段理解这些脚本。

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

这个顺序从最基础的 `prompt + llm + parser` 开始，逐步进入可配置模型、工具定义、Agent 和手动工具调用。

## 脚本索引

- `chat_model_all_params.py`：聚焦 `ChatOpenAI` 的初始化参数和 Runnable 管道写法。
- `langchain_tool_creation_examples.py`：演示 6 种工具定义方式，以及新版 `create_agent()` 的用法。
- `openai_to_deepseek_configurable.py`：演示如何用 `init_chat_model()` 暴露运行时可切换字段。
- `openai_to_deepseek_with_prefix.py`：演示多个模型实例如何用配置前缀隔离运行时参数。
- `test.py`：最基础的 Prompt、模型和输出解析器串联。
- `test2.py`：最简版 `init_chat_model()` 动态配置示例。
- `test3.py`：直接调用 Tavily 搜索，再把结果交给模型总结。
- `test4.py`：让模型触发工具调用，并手工把工具结果接回消息流。

## 核心概念总览

- `ChatOpenAI`：LangChain 里的聊天模型适配器，这里被用来访问 DeepSeek 的 OpenAI 兼容接口。
- `ChatPromptTemplate`：把系统消息和用户消息组织成结构化提示。
- `StrOutputParser`：把模型输出提取成普通字符串。
- `Runnable`：LangChain 把可调用组件抽象成统一接口，支持 `prompt | llm | parser` 这样的组合。
- `tool` / `StructuredTool` / `BaseTool`：LangChain 中向模型暴露工具能力的几种典型方式。
- `create_agent()`：新版 Agent 构造入口，负责把模型、工具和消息流拼成一个可执行图。
- `bind_tools()`：让模型知道自己有哪些工具可以调用。

## 阅读方式建议

每篇独立文档都遵循统一结构：先说明脚本作用和运行前提，再贴出完整代码，然后按自然代码块分段讲解。在分段讲解里，会尽量逐句解释关键语句，并说明这句代码在 Python、LangChain 和第三方库层面分别意味着什么。
```

- [ ] **Step 2: 运行测试，确认 README 校验通过**

Run: `python -m unittest e:\github\python\LangChain\tests\test_langchain_study_docs.py -v`
Expected: PASS for `test_readme_exists_with_core_sections`

- [ ] **Step 3: 提交 README**

```bash
git add e:\github\python\LangChain\docs\LangChain_study\README.md e:\github\python\LangChain\tests\test_langchain_study_docs.py
git commit -m "docs: add langchain study overview"
```

### Task 3: 扩展测试，锁定 4 个核心脚本文档结构

**Files:**
- Modify: `e:\github\python\LangChain\tests\test_langchain_study_docs.py`

- [ ] **Step 1: 为 4 个核心脚本增加失败测试**

```python
    def assert_doc_has_standard_sections(self, file_name: str) -> None:
        path = DOCS_DIR / file_name
        self.assertTrue(path.exists(), f"missing file: {path}")

        text = read_text(path)
        required_sections = [
            "## 脚本作用",
            "## 运行前提",
            "## 完整代码",
            "## 分段讲解",
            "## 执行流程",
            "## 关键对象与机制",
            "## 容易踩坑点",
            "## 可扩展方向",
        ]
        for section in required_sections:
            self.assertIn(section, text, f"{file_name} missing section: {section}")

    def test_core_script_docs_exist_with_standard_sections(self) -> None:
        for file_name in [
            "chat_model_all_params.md",
            "langchain_tool_creation_examples.md",
            "openai_to_deepseek_configurable.md",
            "openai_to_deepseek_with_prefix.md",
        ]:
            self.assert_doc_has_standard_sections(file_name)
```

- [ ] **Step 2: 运行测试，确认它因 4 个核心脚本文档缺失而失败**

Run: `python -m unittest e:\github\python\LangChain\tests\test_langchain_study_docs.py -v`
Expected: FAIL with `missing file: e:\github\python\LangChain\docs\LangChain_study\chat_model_all_params.md`

- [ ] **Step 3: 提交测试扩展**

```bash
git add e:\github\python\LangChain\tests\test_langchain_study_docs.py
git commit -m "test: require core langchain study docs"
```

### Task 4: 编写 4 个核心脚本文档

**Files:**
- Create: `e:\github\python\LangChain\docs\LangChain_study\chat_model_all_params.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\langchain_tool_creation_examples.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\openai_to_deepseek_configurable.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\openai_to_deepseek_with_prefix.md`
- Test: `e:\github\python\LangChain\tests\test_langchain_study_docs.py`

- [ ] **Step 1: 写 `chat_model_all_params.md`**

```markdown
# chat_model_all_params.py 逐句讲解

## 脚本作用

这个脚本展示了如何使用 `langchain_openai.ChatOpenAI` 访问 DeepSeek 的 OpenAI 兼容接口，并把 `ChatPromptTemplate`、模型对象和 `StrOutputParser` 组合成一个 Runnable 链。

## 运行前提

- 已安装 `langchain-openai`、`langchain-core`
- 已设置 `DEEPSEEK_API_KEY`
- 运行环境可以访问 `https://api.deepseek.com`

## 完整代码

这一节直接粘贴 `e:\github\python\LangChain\LangChain_study\chat_model_all_params.py` 当前磁盘版本的完整源码，要求与源文件逐行一致，不删减、不改写、不只摘录片段。

## 分段讲解

先解释导入区：`import os` 用于读取环境变量；`ChatPromptTemplate` 负责把系统消息和人类消息拼装成模型输入；`StrOutputParser` 负责把模型返回值转成纯字符串；`ChatOpenAI` 是 LangChain 对聊天模型的统一封装。

接着解释模型初始化区：`model="deepseek-chat"` 决定调用哪个模型；`api_key=os.getenv("DEEPSEEK_API_KEY")` 表示把鉴权信息从环境变量注入；`base_url` 指向 DeepSeek 的 OpenAI 兼容地址。像 `temperature`、`max_retries`、`top_p` 这类参数都属于模型生成或调用控制参数，文档中要逐项说明它们控制的是采样、重试还是请求层行为。

最后解释链式组合区：`prompt | llm | parser` 使用的是 LangChain Runnable 管道语法，含义是先生成提示消息，再调用模型，最后解析输出文本。这一段必须明确说明它不是操作系统层面的管道，而是 LangChain 对可调用组件的统一组合协议。

## 执行流程

运行脚本后，程序先创建模型对象，再创建提示模板，然后定义输出解析器。随后用 Runnable 管道把三者拼成一条执行链，最后通过 `chain.invoke({"text": "一只小狗_____"})` 把动态变量注入模板并得到最终文本结果。

## 关键对象与机制

- `ChatOpenAI`
- `ChatPromptTemplate`
- `StrOutputParser`
- Runnable 管道语法

## 容易踩坑点

- 如果没有 `DEEPSEEK_API_KEY`，模型调用会失败。
- 如果误把标准库或系统模块里的 `pipe` 当成 LangChain 管道，会出现类型错误。
- 不是所有模型都支持所有初始化参数，文档里要提醒“参数可写”不等于“服务端一定支持”。

## 可扩展方向

- 增加多轮消息模板
- 替换 `StrOutputParser` 为更结构化的输出解析器
- 增加流式输出示例
```

- [ ] **Step 2: 写 `langchain_tool_creation_examples.md`**

```markdown
# langchain_tool_creation_examples.py 逐句讲解

## 脚本作用

这个脚本展示了 LangChain 中多种工具定义方式，并在最后使用新版 `create_agent()` 把模型和工具拼成可执行 Agent。

## 运行前提

- 已安装 `langchain`、`langchain-core`、`langchain-openai`、`pydantic`
- 已设置 `DEEPSEEK_API_KEY`

## 完整代码

这一节直接粘贴 `e:\github\python\LangChain\LangChain_study\langchain_tool_creation_examples.py` 当前磁盘版本的完整源码，要求与源文件逐行一致，不删减、不改写、不只摘录片段。

## 分段讲解

先解释装饰器工具：`@tool` 会把普通 Python 函数包装成 LangChain 工具对象，函数签名和 docstring 会被用来生成工具的名字、参数和描述。

再解释 `WeatherInput(BaseModel)`：这里的 `BaseModel` 来自 `pydantic`，它不仅是类型声明工具，还是运行时参数校验器。`Field(..., description="要查询的城市")` 中的 `...` 表示该字段必填。

在 `EchoTool(BaseTool)` 这一段，必须逐句解释 `name: str = "echo_text"`、`description: str = "把输入文本原样返回。"` 和 `args_schema: Type[BaseModel] = EchoInput`。这里的类型标注不只是写给读者看的，还和 `pydantic v2` 的模型字段识别规则有关；如果没有显式标注，当前版本下会报字段覆盖错误。

在 Agent 构建段，`create_agent(model=llm, tools=tools, system_prompt=...)` 返回的是一个可执行图对象。调用时传入的是 `{"messages": [HumanMessage(...)]}`，这体现了新版 Agent API 以消息流为核心，而不是旧版某些封装里的单一 `input` 字段。

## 执行流程

脚本先定义 6 类工具，然后依次演示它们的直接调用方式。若环境变量存在，再构建 Agent，并让模型自动决定是否调用工具、如何组合工具结果生成最终回答。

## 关键对象与机制

- `@tool`
- `StructuredTool`
- `Tool`
- `BaseTool`
- `RunnableLambda.as_tool()`
- `create_agent()`
- `HumanMessage`

## 容易踩坑点

- `langchain_core.pydantic_v1` 在当前项目版本中不可用。
- 旧版 `AgentExecutor` / `create_tool_calling_agent` 用法与当前版本不兼容。
- `Runnable.as_tool()` 在当前版本会给出 beta 警告，但脚本仍可运行。

## 可扩展方向

- 增加真实搜索工具或数据库工具
- 把工具输入输出改成更严格的结构化 schema
- 演示多工具协作和更复杂的 Agent 消息流
```

- [ ] **Step 3: 写 `openai_to_deepseek_configurable.md` 与 `openai_to_deepseek_with_prefix.md`**

```markdown
# openai_to_deepseek_configurable.py 逐句讲解

## 脚本作用

这个脚本展示如何通过 `init_chat_model()` 创建一个“默认是 OpenAI 风格、但运行时可以切换成 DeepSeek”的聊天模型。

## 运行前提

- 已安装 `langchain`
- 已设置 `DEEPSEEK_API_KEY`

## 完整代码

这一节直接粘贴 `e:\github\python\LangChain\LangChain_study\openai_to_deepseek_configurable.py` 当前磁盘版本的完整源码，要求与源文件逐行一致，不删减、不改写、不只摘录片段。

## 分段讲解

`configurable_fields=(...)` 的作用不是立即修改模型，而是声明“哪些字段允许在调用阶段被覆盖”。`config_prefix="chat"` 的作用是给这些可配置字段统一加前缀，避免在复杂场景中键名冲突。`model.invoke(..., config={"configurable": {...}})` 这一段要逐项解释为什么传的是 `chat_model`、`chat_api_key`、`chat_base_url` 等带前缀的键。

## 执行流程

脚本先定义一个默认的 OpenAI 风格模型配置，再在 `invoke()` 时通过 `configurable` 把目标切换到 DeepSeek，最后打印模型返回内容。

## 关键对象与机制

- `init_chat_model()`
- `configurable_fields`
- `config_prefix`
- `invoke(..., config=...)`

## 容易踩坑点

- `configurable_fields` 决定的是“可覆盖权限”，不是默认值本身。
- `config_prefix` 一旦改动，运行时配置字典里的键名也要一起改。

## 可扩展方向

- 把默认模型从 OpenAI 再切到别的提供商
- 把可配置字段扩展到更多采样参数

# openai_to_deepseek_with_prefix.py 逐句讲解

## 脚本作用

这个脚本展示两个聊天模型实例如何各自拥有独立的运行时配置前缀，从而在同一个 `config` 字典中共存。

## 运行前提

- 已安装 `langchain`
- 已设置 `DEEPSEEK_API_KEY`

## 完整代码

这一节直接粘贴 `e:\github\python\LangChain\LangChain_study\openai_to_deepseek_with_prefix.py` 当前磁盘版本的完整源码，要求与源文件逐行一致，不删减、不改写、不只摘录片段。

## 分段讲解

文档要明确对比 `writer_model` 和 `reviewer_model` 的创建过程，并逐句解释为什么一个使用 `config_prefix="writer"`，另一个使用 `config_prefix="reviewer"`。`runtime_config` 中的 `writer_model`、`reviewer_model`、`writer_temperature`、`reviewer_temperature` 等字段要结合命名规则解释，不要只停留在“这是一份字典配置”。

## 执行流程

脚本先创建两个模型对象，再准备一份公共运行时配置，随后先让 writer 生成文案，再让 reviewer 读取 writer 的输出进行点评。

## 关键对象与机制

- 多模型实例
- 配置前缀隔离
- 运行时共享配置字典

## 容易踩坑点

- 两个模型如果共用无前缀配置，很容易发生键冲突。
- 调用顺序会影响 reviewer 读到的输入内容。

## 可扩展方向

- 增加第三个模型角色
- 演示不同提供商混合共存
```

- [ ] **Step 4: 运行测试，确认 4 个核心脚本文档通过结构校验**

Run: `python -m unittest e:\github\python\LangChain\tests\test_langchain_study_docs.py -v`
Expected: PASS for `test_readme_exists_with_core_sections` and `test_core_script_docs_exist_with_standard_sections`

- [ ] **Step 5: 提交核心文档**

```bash
git add e:\github\python\LangChain\docs\LangChain_study\README.md e:\github\python\LangChain\docs\LangChain_study\chat_model_all_params.md e:\github\python\LangChain\docs\LangChain_study\langchain_tool_creation_examples.md e:\github\python\LangChain\docs\LangChain_study\openai_to_deepseek_configurable.md e:\github\python\LangChain\docs\LangChain_study\openai_to_deepseek_with_prefix.md e:\github\python\LangChain\tests\test_langchain_study_docs.py
git commit -m "docs: add core langchain study guides"
```

### Task 5: 扩展测试，锁定 4 个 test 脚本文档结构

**Files:**
- Modify: `e:\github\python\LangChain\tests\test_langchain_study_docs.py`

- [ ] **Step 1: 增加 4 个 test 脚本文档的失败测试**

```python
    def test_test_script_docs_exist_with_standard_sections(self) -> None:
        for file_name in [
            "test.md",
            "test2.md",
            "test3.md",
            "test4.md",
        ]:
            self.assert_doc_has_standard_sections(file_name)
```

- [ ] **Step 2: 运行测试，确认它因 `test.md` 等文件缺失而失败**

Run: `python -m unittest e:\github\python\LangChain\tests\test_langchain_study_docs.py -v`
Expected: FAIL with `missing file: e:\github\python\LangChain\docs\LangChain_study\test.md`

- [ ] **Step 3: 提交测试扩展**

```bash
git add e:\github\python\LangChain\tests\test_langchain_study_docs.py
git commit -m "test: require langchain study practice docs"
```

### Task 6: 编写 4 个 test 脚本文档并做最终回归

**Files:**
- Create: `e:\github\python\LangChain\docs\LangChain_study\test.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\test2.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\test3.md`
- Create: `e:\github\python\LangChain\docs\LangChain_study\test4.md`
- Test: `e:\github\python\LangChain\tests\test_langchain_study_docs.py`

- [ ] **Step 1: 写 `test.md` 与 `test2.md`**

```markdown
# test.py 逐句讲解

## 脚本作用

这个脚本是整套示例中最基础的链式调用示例，核心目标是让读者理解 Prompt、模型和输出解析器是如何串起来的。

## 运行前提

- 已安装 `langchain`、`langchain-core`、`langchain-openai`
- 已设置 `DEEPSEEK_API_KEY`

## 完整代码

这一节直接粘贴 `e:\github\python\LangChain\LangChain_study\test.py` 当前磁盘版本的完整源码，要求与源文件逐行一致，不删减、不改写、不只摘录片段。

## 分段讲解

重点解释导入、模型初始化、提示模板、`StrOutputParser` 和 `RunnableSequence[Any, Any](prompt, llm, parser)`。文档要特别说明 `RunnableSequence` 的类型参数只是类型提示，不会改变运行时语义。

## 执行流程

脚本先创建模型，再定义一个翻译任务提示模板，然后把链执行一次并打印中文结果。

## 关键对象与机制

- `RunnableSequence`
- `ChatPromptTemplate`
- `StrOutputParser`

## 容易踩坑点

- 忘记设置 API Key 会导致模型调用失败。
- 如果读者把 `RunnableSequence` 和 `|` 管道写法当成两套不同机制，会理解偏差；文档里要解释它们本质上都在组合 Runnable。

## 可扩展方向

- 把翻译任务改成摘要或改写
- 改用 `prompt | llm | parser` 管道写法

# test2.py 逐句讲解

## 脚本作用

这个脚本演示 `init_chat_model()` 的最简配置化调用方式：默认模型先建好，调用时再通过 `configurable` 动态覆盖参数。

## 运行前提

- 已安装 `langchain`
- 已设置 `DEEPSEEK_API_KEY`

## 完整代码

这一节直接粘贴 `e:\github\python\LangChain\LangChain_study\test2.py` 当前磁盘版本的完整源码，要求与源文件逐行一致，不删减、不改写、不只摘录片段。

## 分段讲解

重点逐句解释 `configurable_fields` 元组、默认参数与运行时覆盖参数的关系，以及 `config={"configurable": {...}}` 的字典层级结构。

## 执行流程

脚本先定义一个 DeepSeek 模型，再在调用时覆盖 `max_tokens`、`temperature`、`top_p` 等参数，最后打印回答。

## 关键对象与机制

- `init_chat_model()`
- `configurable`
- 运行时参数覆盖

## 容易踩坑点

- 没有把字段列进 `configurable_fields` 的参数，运行时无法覆盖。

## 可扩展方向

- 增加更多可调参数
- 对比默认值与运行时值的差异
```

- [ ] **Step 2: 写 `test3.md` 与 `test4.md`**

```markdown
# test3.py 逐句讲解

## 脚本作用

这个脚本展示一种“先搜再总结”的常见模式：先让 Tavily 返回搜索结果，再把这些结果交给 DeepSeek 做中文总结。

## 运行前提

- 已安装 `langchain-community`、`langchain-openai`
- 已设置 `DEEPSEEK_API_KEY`
- 已设置 `TAVILY_API_KEY`

## 完整代码

这一节直接粘贴 `e:\github\python\LangChain\LangChain_study\test3.py` 当前磁盘版本的完整源码，要求与源文件逐行一致，不删减、不改写、不只摘录片段。

## 分段讲解

要重点解释 `TavilySearchResults(max_results=3)` 是如何构造搜索工具的，`search_tool.invoke({"query": query})` 为什么传的是字典，以及为什么搜索结果最终要 `str(search_result)` 再注入提示模板。

## 执行流程

脚本先调用搜索工具拿到外部资料，再构造总结提示词，让模型基于检索结果输出摘要。

## 关键对象与机制

- `TavilySearchResults`
- 搜索结果到提示词的转换
- `prompt | llm`

## 容易踩坑点

- 缺少 `TAVILY_API_KEY` 会导致搜索失败。
- 当前 Tavily 接口在 `langchain-community` 中会出现弃用警告，文档里要说明这是版本层面的提醒，不是脚本立即失效。

## 可扩展方向

- 把搜索结果做结构化筛选
- 改成多轮追问总结

# test4.py 逐句讲解

## 脚本作用

这个脚本展示更贴近 Agent 内部机制的做法：把工具绑定给模型，让模型自己决定何时发起工具调用，然后由程序手工接回工具结果。

## 运行前提

- 已安装 `langchain`、`langchain-community`
- 已设置 `DEEPSEEK_API_KEY`
- 已设置 `TAVILY_API_KEY`

## 完整代码

这一节直接粘贴 `e:\github\python\LangChain\LangChain_study\test4.py` 当前磁盘版本的完整源码，要求与源文件逐行一致，不删减、不改写、不只摘录片段。

## 分段讲解

文档必须逐句解释 `llm.bind_tools([search_tool])`、`first_response.tool_calls`、`ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])`。重点说明这里展示的是“消息流层面的工具调用协议”，不是单纯的函数调用。

## 执行流程

脚本先向模型发送用户问题，如果模型请求调用工具，程序就执行真实工具，再把工具结果封装成 `ToolMessage` 追加回消息列表，最后再次调用模型得到最终回答。

## 关键对象与机制

- `bind_tools()`
- `HumanMessage`
- `ToolMessage`
- `tool_calls`

## 容易踩坑点

- 如果不把工具返回值封装成 `ToolMessage` 并带上正确的 `tool_call_id`，模型无法把工具结果和先前的工具请求对应起来。
- 这类脚本对消息顺序非常敏感，少追加一步都会影响最终结果。

## 可扩展方向

- 支持多个不同工具
- 把手工消息流封装成通用函数
```

- [ ] **Step 3: 运行最终测试**

Run: `python -m unittest e:\github\python\LangChain\tests\test_langchain_study_docs.py -v`
Expected: PASS with all three tests green

- [ ] **Step 4: 手工抽查文档与脚本一致性**

Run: `python -c "from pathlib import Path; print(sorted([p.name for p in Path(r'e:\github\python\LangChain\docs\LangChain_study').glob('*.md')]))"`
Expected: 打印 9 个 markdown 文件名，且包含 `README.md` 和 8 个脚本文档

- [ ] **Step 5: 提交全部文档**

```bash
git add e:\github\python\LangChain\docs\LangChain_study\README.md e:\github\python\LangChain\docs\LangChain_study\chat_model_all_params.md e:\github\python\LangChain\docs\LangChain_study\langchain_tool_creation_examples.md e:\github\python\LangChain\docs\LangChain_study\openai_to_deepseek_configurable.md e:\github\python\LangChain\docs\LangChain_study\openai_to_deepseek_with_prefix.md e:\github\python\LangChain\docs\LangChain_study\test.md e:\github\python\LangChain\docs\LangChain_study\test2.md e:\github\python\LangChain\docs\LangChain_study\test3.md e:\github\python\LangChain\docs\LangChain_study\test4.md e:\github\python\LangChain\tests\test_langchain_study_docs.py
git commit -m "docs: add langchain study walkthroughs"
```
