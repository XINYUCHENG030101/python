# openai_to_deepseek_with_prefix.py 逐句讲解

## 脚本作用

这个脚本是在前一个“可配置模型”示例基础上继续前进一步：它不再只有一个模型对象，而是同时创建两个模型角色 `writer` 和 `reviewer`，并通过不同的配置前缀让它们共享一份运行时配置字典但互不冲突。

这个例子非常适合理解 `config_prefix` 的真正价值。

## 运行前提

- 已安装 `langchain`
- 已设置环境变量 `DEEPSEEK_API_KEY`
- 当前网络可以访问 `https://api.deepseek.com`

## 完整代码

```python
import os

from langchain.chat_models import init_chat_model


# 第一个模型：writer。
# 通过 config_prefix="writer" 给所有可配置字段加上 writer_ 前缀。
writer_model = init_chat_model(
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
    config_prefix="writer",
    temperature=0.7,
    max_tokens=100,
)


# 第二个模型：reviewer。
# 通过 config_prefix="reviewer" 给所有可配置字段加上 reviewer_ 前缀。
reviewer_model = init_chat_model(
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
    config_prefix="reviewer",
    temperature=0.2,
    max_tokens=120,
)


# 这里准备一份公共配置，两个模型都切换到 DeepSeek。
# 因为前缀不同，所以 writer 和 reviewer 的配置键不会冲突。
runtime_config = {
    "configurable": {
        "writer_model": "deepseek-chat",
        "writer_model_provider": "openai",
        "writer_api_key": os.getenv("DEEPSEEK_API_KEY"),
        "writer_base_url": "https://api.deepseek.com",
        "writer_temperature": 0.8,
        "writer_max_tokens": 80,
        "writer_top_p": 0.9,
        "writer_presence_penalty": 0.2,
        "writer_frequency_penalty": 0.1,
        "writer_stop": None,
        "reviewer_model": "deepseek-chat",
        "reviewer_model_provider": "openai",
        "reviewer_api_key": os.getenv("DEEPSEEK_API_KEY"),
        "reviewer_base_url": "https://api.deepseek.com",
        "reviewer_temperature": 0.2,
        "reviewer_max_tokens": 100,
        "reviewer_top_p": 0.7,
        "reviewer_presence_penalty": 0.0,
        "reviewer_frequency_penalty": 0.0,
        "reviewer_stop": None,
    }
}


# 第一次调用：writer 模型生成一句文案。
writer_resp = writer_model.invoke(
    "请写一句关于春天的短句。",
    config=runtime_config,
)

# 第二次调用：reviewer 模型对 writer 的输出做一句点评。
reviewer_resp = reviewer_model.invoke(
    f"请用一句话点评这句文案：{writer_resp.content}",
    config=runtime_config,
)

print("writer 输出：")
print(writer_resp.content)
print()
print("reviewer 输出：")
print(reviewer_resp.content)
```

## 分段讲解

### 导入区

- `import os` 仍然用于读取环境变量。
- `init_chat_model` 仍然是本脚本的核心入口，因为它支持运行时配置覆盖。

### 第一个模型：`writer_model`

```python
writer_model = init_chat_model(
    "gpt-4o-mini",
    model_provider="openai",
    configurable_fields=(...),
    config_prefix="writer",
    temperature=0.7,
    max_tokens=100,
)
```

- `writer_model` 这个名字本身就体现了角色语义：它负责“生成文案”。
- `config_prefix="writer"` 是本段最重要的参数。它决定之后运行时覆盖字段的命名空间都会以 `writer_` 开头。
- `temperature=0.7` 和 `max_tokens=100` 是 writer 的默认值，倾向于生成更有表现力的内容。

### 第二个模型：`reviewer_model`

```python
reviewer_model = init_chat_model(
    ...
    config_prefix="reviewer",
    temperature=0.2,
    max_tokens=120,
)
```

- `reviewer_model` 这个名字表示它承担“点评者”的角色。
- `config_prefix="reviewer"` 说明它的运行时字段将全部以 `reviewer_` 开头。
- `temperature=0.2` 比 writer 更低，意味着 reviewer 更偏稳定、收敛、克制的输出风格。

### 公共运行时配置区

```python
runtime_config = {
    "configurable": {
        "writer_model": "deepseek-chat",
        ...
        "reviewer_model": "deepseek-chat",
        ...
    }
}
```

- 这里构造的是一个单独的 Python 字典，而不是分别给两个模型写两份配置。
- `runtime_config` 之所以能同时服务两个模型，是因为键名被前缀隔离了。

### `writer_*` 这一组字段

- `writer_model`：覆盖 writer 的默认模型名。
- `writer_model_provider`：仍然使用 OpenAI 兼容接口风格。
- `writer_api_key` 和 `writer_base_url`：把 writer 的请求目标切到 DeepSeek。
- `writer_temperature`、`writer_max_tokens`、`writer_top_p` 等：调整 writer 的生成行为，让它更适合写文案。

### `reviewer_*` 这一组字段

- `reviewer_model`、`reviewer_model_provider`、`reviewer_api_key`、`reviewer_base_url`：同样把 reviewer 切到 DeepSeek。
- `reviewer_temperature=0.2`、`reviewer_top_p=0.7`：让 reviewer 更稳定、更收敛，适合做点评而不是发挥。

### 两次调用区

```python
writer_resp = writer_model.invoke(
    "请写一句关于春天的短句。",
    config=runtime_config,
)
```

- 这里让 writer 先执行一次，输入是“写一句关于春天的短句”。
- `config=runtime_config` 表示 writer 调用时会去读取其中的 `writer_*` 字段。

```python
reviewer_resp = reviewer_model.invoke(
    f"请用一句话点评这句文案：{writer_resp.content}",
    config=runtime_config,
)
```

- 这里使用 Python f-string 把 `writer_resp.content` 插入到 reviewer 的提示词里。
- reviewer 再次使用同一份 `runtime_config`，但它会读取 `reviewer_*` 字段，而不是 `writer_*` 字段。

### 输出区

- `print("writer 输出：")`、`print(writer_resp.content)`：打印 writer 的结果。
- `print()`：打印空行，让控制台输出更清晰。
- `print("reviewer 输出：")`、`print(reviewer_resp.content)`：打印 reviewer 的结果。

## 执行流程

脚本先创建两个模型对象，一个承担写作者角色，一个承担点评者角色。虽然它们的默认配置都基于 OpenAI 风格模型，但在真正调用时，二者都会通过 `runtime_config` 切换到 DeepSeek。第一次调用由 writer 生成一句春天文案，第二次调用由 reviewer 读取 writer 的结果并输出点评，最后把两段文本分别打印出来。

## 关键对象与机制

- 多模型实例：同一脚本里可以同时存在多个模型对象，每个对象都有自己的角色。
- `config_prefix`：通过前缀让不同模型实例共享一份配置字典而不冲突。
- `runtime_config`：把运行时覆盖参数集中管理，便于统一传递和维护。
- 角色分工：writer 负责生成，reviewer 负责评价，这是多模型协作的一个最小原型。

## 容易踩坑点

- 如果两个模型都不加前缀，那么运行时字段就会冲突，脚本无法区分哪组参数给谁用。
- reviewer 的输入依赖 `writer_resp.content`，所以执行顺序不能颠倒。
- `model_provider="openai"` 在这里仍然描述的是接口协议风格，而不是服务商品牌。
- 两个模型虽然共享同一份配置字典，但默认参数和运行时参数都可以不同，不要混淆“共用配置对象”和“配置值完全相同”。

## 可扩展方向

- 增加第三个角色，比如 editor，对 writer 和 reviewer 的结果继续加工。
- 把不同角色切到不同提供商，演示真正的跨模型协作。
- 把这套模式扩展成多轮生成与多轮评审工作流。
