# openai_to_deepseek_configurable.py 逐句讲解

## 脚本作用

这个脚本展示的是 LangChain 中非常值得学习的一种思路：先定义一个“默认配置”的聊天模型，再在真正调用时通过 `configurable` 字段覆盖掉关键参数，让同一个模型对象在运行时切换到别的服务提供商配置。

在这个例子里，默认模型被写成 OpenAI 风格，但真正调用时切换成了 DeepSeek。

## 运行前提

- 已安装 `langchain`
- 已设置环境变量 `DEEPSEEK_API_KEY`
- 当前网络可以访问 `https://api.deepseek.com`

## 完整代码

```python
import os

from langchain.chat_models import init_chat_model


# 默认先创建一个 OpenAI 风格的模型配置。
# 注意：这里只是默认配置成 openai 风格，真正调用时会通过 configurable_fields 切到 DeepSeek。
model = init_chat_model(
    "gpt-4o-mini",
    model_provider="openai",
    configurable_fields=(
        "model",
        "model_provider",
        "api_key",
        "base_url",
        "temperature",
        "max_tokens",
        "top_p",
        "presence_penalty",
        "frequency_penalty",
        "stop",
    ),
    config_prefix="chat",
    temperature=0.7,
    max_tokens=100,
)


# 在本次调用中，把默认的 openai 模型切换成 DeepSeek。
resp = model.invoke(
    "请用一句话介绍你自己。",
    config={
        "configurable": {
            "chat_model": "deepseek-chat",
            "chat_model_provider": "openai",
            "chat_api_key": os.getenv("DEEPSEEK_API_KEY"),
            "chat_base_url": "https://api.deepseek.com",
            "chat_temperature": 0.3,
            "chat_max_tokens": 60,
            "chat_top_p": 0.8,
            "chat_presence_penalty": 0.1,
            "chat_frequency_penalty": 0.1,
            "chat_stop": None,
        }
    },
)

print(resp.content)
```

## 分段讲解

### 导入区

- `import os` 用于读取环境变量。
- `from langchain.chat_models import init_chat_model` 导入模型初始化辅助函数。这个函数比直接实例化某个具体类更适合演示“运行时可切换配置”的能力。

### 默认模型配置区

```python
model = init_chat_model(
    "gpt-4o-mini",
    model_provider="openai",
    configurable_fields=(...),
    config_prefix="chat",
    temperature=0.7,
    max_tokens=100,
)
```

- `init_chat_model(...)` 可以理解为“创建一个 LangChain 统一模型对象”，而不是死绑定某个固定 Python 类。
- 第一个位置参数 `"gpt-4o-mini"` 是默认模型名。这里的“默认”非常关键，因为它后面是允许被覆盖的。
- `model_provider="openai"` 指定默认提供商类别。它不是说最终只能调用 OpenAI，而是说当前默认解释方式走 OpenAI 风格。
- `configurable_fields=(...)` 是本脚本的重点之一。它声明“这些字段可以在运行时被覆盖”。
- 这一组字段里包含了：
  - 模型身份相关字段：`model`、`model_provider`
  - 连接和鉴权相关字段：`api_key`、`base_url`
  - 生成控制字段：`temperature`、`max_tokens`、`top_p`、`presence_penalty`、`frequency_penalty`、`stop`
- `config_prefix="chat"` 的作用是给所有可配置字段统一加前缀。也就是说，运行时传参时不能直接写 `model`，而要写 `chat_model`。
- `temperature=0.7` 和 `max_tokens=100` 是默认值。它们不是最终强制值，因为后面会在 `invoke()` 阶段被覆盖。

### 运行时覆盖区

```python
resp = model.invoke(
    "请用一句话介绍你自己。",
    config={
        "configurable": {
            "chat_model": "deepseek-chat",
            ...
        }
    },
)
```

- `model.invoke(...)` 是同步调用入口。
- 第一个参数 `"请用一句话介绍你自己。"` 是用户输入内容。
- 第二个关键参数 `config={...}` 不是提示词内容，而是运行时配置字典。
- `configurable` 是 LangChain 约定的特殊键，用来承载这些“允许在调用时覆盖”的字段。

### `configurable` 字典逐句理解

- `"chat_model": "deepseek-chat"`：覆盖默认模型名。注意键名不是 `model`，而是 `chat_model`，因为前面设置了 `config_prefix="chat"`。
- `"chat_model_provider": "openai"`：这里仍然写 `openai`，因为 DeepSeek 使用的是 OpenAI 兼容接口协议。
- `"chat_api_key": os.getenv("DEEPSEEK_API_KEY")`：运行时注入 DeepSeek 的真实 API Key。
- `"chat_base_url": "https://api.deepseek.com"`：运行时把目标地址改成 DeepSeek。
- `"chat_temperature": 0.3`：覆盖默认采样温度。
- `"chat_max_tokens": 60`：覆盖默认最大输出长度。
- `"chat_top_p"`、`"chat_presence_penalty"`、`"chat_frequency_penalty"`：继续覆盖生成控制参数。
- `"chat_stop": None`：显式说明本次没有停止词。

### 输出区

```python
print(resp.content)
```

- `resp` 是模型返回的消息对象。
- `.content` 表示消息文本内容。
- 这里没有使用 `StrOutputParser`，因为脚本想直接展示消息对象最核心的文本字段。

## 执行流程

脚本先通过 `init_chat_model()` 创建一个默认的 OpenAI 风格模型对象，并且声明哪些字段允许在调用阶段被覆盖。然后在 `invoke()` 时传入 `config={"configurable": ...}`，把默认模型切换成 DeepSeek 的兼容接口配置。最后脚本打印模型返回文本。

## 关键对象与机制

- `init_chat_model()`：适合需要统一初始化和运行时覆盖的场景。
- `configurable_fields`：决定哪些字段能在调用阶段动态改写。
- `config_prefix`：为运行时覆盖字段加命名空间，避免复杂场景下键名冲突。
- `invoke(..., config=...)`：把“模型输入”和“运行时配置”同时交给 LangChain。

## 容易踩坑点

- 如果某个字段没有写进 `configurable_fields`，你在 `configurable` 里传它通常不会生效。
- `config_prefix` 一旦设置，运行时键名必须带前缀，否则 LangChain 找不到对应字段。
- `model_provider="openai"` 很容易让人误解成“只能用 OpenAI”，实际上这里描述的是接口协议风格。
- 如果 `DEEPSEEK_API_KEY` 为空，切换后的调用仍然会失败。

## 可扩展方向

- 增加更多可配置字段，例如超时、重试或额外请求体参数。
- 把默认模型再切到别的提供商，形成统一配置接口。
- 对比“不使用 `configurable_fields`”和“使用 `configurable_fields`”的差异，帮助理解 LangChain 的配置边界。
