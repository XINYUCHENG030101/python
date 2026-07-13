# test2.py 逐句讲解

## 脚本作用

`test2.py` 演示的是 `init_chat_model()` 的最简配置化用法：先创建一个 DeepSeek 模型对象，再在调用时用 `configurable` 覆盖部分默认参数。

它比 `openai_to_deepseek_configurable.py` 更简单，适合作为“运行时参数覆盖”概念的入门版。

## 运行前提

- 已安装 `langchain`
- 已设置环境变量 `DEEPSEEK_API_KEY`
- 当前网络可以访问 `https://api.deepseek.com`

## 完整代码

```python
import os

from langchain.chat_models import init_chat_model


deep_model = init_chat_model(
    "deepseek-chat",
    model_provider="openai",
    configurable_fields=(
        "max_tokens",
        "temperature",
        "top_p",
        "presence_penalty",
        "frequency_penalty",
    ),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

resp = deep_model.invoke(
    "请用一句话介绍 LangChain。",
    config={
        "configurable": {
            "max_tokens": 50,
            "temperature": 0.3,
            "top_p": 0.8,
            "presence_penalty": 0.2,
            "frequency_penalty": 0.2,
        }
    },
)

print(resp.content)
```

## 分段讲解

### 导入区

- `import os` 用于读取环境变量。
- `init_chat_model` 是这个脚本的核心函数，它负责生成一个可调用的聊天模型对象。

### 模型初始化区

```python
deep_model = init_chat_model(
    "deepseek-chat",
    model_provider="openai",
    configurable_fields=(...),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
```

- `deep_model` 是变量名，表示当前脚本要使用的聊天模型对象。
- `"deepseek-chat"` 是默认模型名。
- `model_provider="openai"` 说明调用协议按照 OpenAI 兼容接口风格处理。
- `configurable_fields=(...)` 表示这些字段允许在运行时通过 `configurable` 覆盖。
- 这里放进去的都是生成控制参数，例如 `max_tokens`、`temperature`、`top_p`。
- `api_key` 和 `base_url` 在这里是固定死的，不像前面更复杂的示例那样也纳入运行时覆盖。

### 调用区

```python
resp = deep_model.invoke(
    "请用一句话介绍 LangChain。",
    config={
        "configurable": {
            "max_tokens": 50,
            "temperature": 0.3,
            "top_p": 0.8,
            "presence_penalty": 0.2,
            "frequency_penalty": 0.2,
        }
    },
)
```

- 第一个参数是用户输入文本。
- `config={...}` 是运行时附加配置。
- `configurable` 是一个约定键，内部字典中写的字段必须已经出现在 `configurable_fields` 里。
- `"max_tokens": 50` 限制本次输出长度。
- `"temperature": 0.3` 让输出更稳定。
- `"top_p": 0.8` 控制核采样范围。
- `"presence_penalty"` 和 `"frequency_penalty"` 控制内容新颖度与重复度。

### 输出区

```python
print(resp.content)
```

- `resp` 是返回的消息对象。
- `.content` 提取消息文本。

## 执行流程

脚本先创建一个指向 DeepSeek 的聊天模型对象，并声明允许在运行时覆盖的生成参数。然后脚本调用模型，同时传入用户问题和一组 `configurable` 参数，用这组参数覆盖默认值。最后把返回文本打印出来。

## 关键对象与机制

- `init_chat_model()`：创建统一的聊天模型对象。
- `configurable_fields`：决定可被动态覆盖的字段集合。
- `config={"configurable": ...}`：在单次调用里临时改写这些参数。

## 容易踩坑点

- 没有被声明到 `configurable_fields` 中的字段，不能指望在 `configurable` 里直接覆盖。
- 这里虽然写的是 `model_provider="openai"`，但并不意味着目标服务一定是 OpenAI 官方。
- `api_key` 和 `base_url` 在这个脚本里没有作为可配置字段暴露出去，所以这里只能覆盖生成参数，不能像更复杂示例那样切换服务目标。

## 可扩展方向

- 把 `api_key` 和 `base_url` 也纳入可配置字段。
- 比较不同 `temperature` 和 `top_p` 对结果风格的影响。
- 和 `openai_to_deepseek_configurable.py` 对照阅读，理解“最简配置化”和“完整配置化”的区别。
