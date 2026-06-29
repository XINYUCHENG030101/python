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
