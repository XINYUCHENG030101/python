import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


# 这个文件演示 ChatOpenAI 在当前本地版本下，创建聊天模型时常用/可填写的初始化参数。
# 这里以 DeepSeek 为例，因为 DeepSeek 提供的是 OpenAI 兼容接口，所以仍然使用 ChatOpenAI。

llm = ChatOpenAI(
    model="deepseek-chat",  # 模型名称。这里选择 DeepSeek 的聊天模型。
    temperature=0.7,  # 采样温度。越大越发散，越小越稳定。
    model_kwargs={},  # 其他未被显式声明的底层模型参数，按字典传入。
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # API Key。这里从环境变量读取。
    base_url="https://api.deepseek.com",  # 接口基地址。使用 DeepSeek 时需要改成它的地址。
    organization=None,  # OpenAI 组织 ID。通常只在 OpenAI 官方平台下使用，DeepSeek 一般不填。
    openai_proxy=None,  # 代理地址。走代理时可填写；不要和自定义 http_client/http_async_client 同时使用。
    timeout=None,  # 请求超时时间。可填数字秒数，也可填更详细的超时配置对象。
    max_retries=2,  # 请求失败后的最大重试次数。
    presence_penalty=None,  # 存在惩罚。鼓励模型谈论新内容，减少重复旧话题。
    frequency_penalty=None,  # 频率惩罚。降低高频重复词再次出现的概率。
    seed=None,  # 随机种子。部分模型/服务支持后可提升结果复现性。
    logprobs=None,  # 是否返回 token 的对数概率信息。
    top_logprobs=None,  # 返回每个位置概率最高的若干 token；通常要求同时开启 logprobs。
    logit_bias=None,  # 调整某些 token 被采样的倾向，键一般是 token id，值是偏置强度。
    streaming=False,  # 是否开启流式输出。True 时可逐段接收模型回复。
    n=1,  # 每次请求返回几个候选结果。流式输出时必须为 1。
    top_p=None,  # 核采样参数。和 temperature 类似，一般二选一调节即可。
    max_tokens=None,  # 本次最多生成多少 token。None 表示使用服务端默认策略。
    tiktoken_model_name=None,  # 仅用于本地 token 计数时指定模型名，通常不用填。
    default_headers=None,  # 每次请求默认附带的 HTTP 头。
    default_query=None,  # 每次请求默认附带的查询参数。
    http_client=None,  # 自定义同步 http 客户端。若自定义异步客户端，通常也要一起配置。
    http_async_client=None,  # 自定义异步 http 客户端。若自定义同步客户端，通常也要一起配置。
    stop_sequences=None,  # 停止词。模型生成到这些内容时会提前停止。
    extra_body=None,  # 额外补充到请求 JSON 中的字段，常用于某些 OpenAI 兼容服务扩展参数。
    include_response_headers=False,  # 是否把响应头放进返回结果的 metadata 中。
)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "请扩充这段故事，要求字数10个字以内"),
        ("human", "{text}"),
    ]
)

parser = StrOutputParser()

# 使用 LangChain Runnable 语法按顺序组合 prompt、llm 和 parser。
# 这里不能使用 `nt.pipe`，否则会调用到操作系统模块里的同名函数。
chain = prompt | llm | parser
resp = chain.invoke({"text": "一只小狗_____"})
print(resp)
