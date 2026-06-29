from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 1. 定义OpenAI模型
# model = ChatOpenAI(
#     model="gpt-4o-mini",
#     # temperature=2,       # 采样温度
#     # max_tokens=10,     # 最大 token 数
#     # timeout=None,      # 超时时间
#     # max_retries=2,     # 最大重试次数
#     # api_key="...",      # 指定 api key
#     # base_url="...",     # 指定前置请求路径
#     # organization="...", # openai 组织 IA
#     # other params...
# )
model = ChatOpenAI(
    model="deepseek-chat",
    api_key="sk-a5b3406086ec4c89832442954c60f210",      # 指定 api key
    base_url="https://api.deepseek.com/v1",     # 指定前置请求路径
)

# 2. 定义消息
messages = [
    SystemMessage(content="请补全一段故事，100个字以内："),
    HumanMessage(content="一只猫正在__？")
]
# print(model.invoke(messages))


# 3. 定义输出解析器组件
parser = StrOutputParser()

# 4. 定义链
# 执行链
chain = model | parser
print(chain.invoke(messages))





