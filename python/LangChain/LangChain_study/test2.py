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
