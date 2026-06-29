from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 定义聊天模型
model = ChatOpenAI(model="gpt-4o-mini")
# 定义嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# 配置 Redis 客户端
redis_url = "redis://192.168.100.238:6379"
config = RedisConfig(
    index_name="qa",
    redis_url=redis_url,
    metadata_schema=[
        {"name": "category", "type": "tag"},
        {"name": "num", "type": "numeric"},
    ],
)
# 定义 Redis 向量存储
vector_store = RedisVectorStore(embeddings, config=config)
# 生成检索器
retriever = vector_store.as_retriever()

# 定义提示词模板
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "human",
            """你是负责回答问题的助手。使用以下检索到的上下文片段来回答问题。如果你不知道答案，就说你不知道。最多只用三句话，回答要简明扼要。
Question: {question}
Context: {context}
Answer:""",
        ),
    ]
)

# 将文档转换为字符串
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 定义链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# 循环输入问题
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
    chunks = []
    for chunk in rag_chain.stream(question):
        chunks.append(chunk)
        print(chunk, end="", flush=True)
    print()  # 换行