from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_redis import RedisConfig, RedisVectorStore

# 构建链：完成RAG能力
# 定义组件，构建链

# 嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# 聊天模型
model = ChatOpenAI(model="gpt-4o-mini")

# 1. 先从知识库中检索
# Redis 配置
config = RedisConfig(
    index_name="qa",  # 定义索引名
    redis_url="redis://192.168.100.238:6379",
    metadata_schema=[
        {"name": "category", "type": "tag"},   # 添加索引字段：分类
        {"name": "num", "type": "numeric"},    # 添加索引字段：编号
    ]
)
# Redis 向量库
vector_store = RedisVectorStore(
    embeddings=embeddings,
    config=config,
)
# 检索器
retriever = vector_store.as_retriever()

# 2. 将检索结果+查询语句 构建为提示词（提示词模板）

# 提示词模板
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "human",
            """你是负责回答问题的助手。使用一下检索到的上下文片段来回答问题。如果你不知道答案，就说不知道答案。最多回复三句话的结果，回答要简明扼要
            Question:{question}
            Context:{context}
            Answer:"""
        )
    ]
)

# 将检索出来的文档转换成文本传递给提示词模板
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 3. 将消息发送给 LLM（实例化消息，交由链完成）

# 定义链，执行时需要 question
# 检索器 + format_docs， question （同时传递）
# prompt
# model
# 输出解析器
chain = (
    # 检索器 + format_docs 分支1
    # question            分支2: RunnablePassthrough() 在链中透传输入数据，保持原始问题不变，直接传递给后续步骤
    {"context":  retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()   # 输出解析器
)

# 执行流：
# 输入问题："项目介绍"
# 并行执行两个分支，提高效率
# 输出结果：
# {
#    "context":"xxxx"
#    "question":"项目介绍"
# }


# 4. 打印字符串结果 （流式）
while True:
    # 获取用户输入
    question = input("\n请输入您的问题（输入'退出'或'quit'结束程序）: ").strip()

    # 检查是否退出
    if question.lower() in ["退出", "quit"]:
        print("程序已结束，再见！")
        break

    # 检查输入是否为空
    if not question:
        print("问题不能为空，请重新输入。")
        continue

    # 执行链，流式输出
    print("回答: ", end="", flush=True)
    for chunk in chain.stream(question):
        print(chunk, end="", flush=True)
    print()  # 换行