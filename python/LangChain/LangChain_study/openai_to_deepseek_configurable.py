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
