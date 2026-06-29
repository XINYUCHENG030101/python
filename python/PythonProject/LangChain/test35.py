from typing import List

from langchain_core.documents import Document
from langchain_core.runnables import chain
from langchain_openai import OpenAIEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore

# 嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Redis 配置
config = RedisConfig(
    index_name="qa",  # 定义索引名
    redis_url="redis://192.168.100.238:6379",
    metadata_schema=[
        {"name": "category", "type": "tag"},   # 添加索引字段：分类
        {"name": "num", "type": "numeric"},    # 添加索引字段：编号
    ]
)

# 初始化 Redis 向量存储实例（建立了索引结构）
vector_store = RedisVectorStore(
    embeddings=embeddings,
    config=config,
)

# 检索器依赖向量库(Runnable)
# retriever = vector_store.as_retriever(search_kwargs={"k" : 2})

#
# 使用@chain，定义检索器函数，当作具有Runnable的"检索器"使用
@chain
def retriever(query: str) -> List[Document]:
    return vector_store.similarity_search(query=query ,k=2)


search_docs = retriever.invoke("项目介绍")
for doc in search_docs:
    print("*" * 30)
    print(doc.page_content)