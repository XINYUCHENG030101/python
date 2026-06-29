from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_openai import OpenAIEmbeddings
from langchain_redis import RedisVectorStore, RedisConfig
from langchain_text_splitters import CharacterTextSplitter
from redisvl.query.filter import Tag, Num

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

# CRUD

# single 模式，只生成一个大文档
# loader = UnstructuredMarkdownLoader("../Docs/markdown/脚手架级微服务租房平台Q&A.md",)
# # Document 列表
# data = loader.load()
#
# # tiktoken 分词器
# text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
#     encoding_name="cl100k_base", # cl100k_base 是tiktoken 分词器中的一种编码方式
#     chunk_size=400,              # 块token大小(参考标准，为了保证段落/句子完整，会超出此设定的大小)
#     chunk_overlap=50,            # 块重叠大小
# )
#
# # 文档列表
# docs = text_splitter.split_documents(data)
# for i, doc in enumerate(docs, start=1):
#     doc.metadata["category"] = "QA"
#     doc.metadata["num"] = i

# 添加文档（编制索引）
# ids = vector_store.add_documents(documents=docs)
# print(f"编制了{len(ids)}个索引")
# print(f"前三个索引是：{ids[:3]}")

# # 查
# print(vector_store.get_by_ids(["01K85F9HDK4H98QK221YA2ZQ7E"]))
#
# # 删除
# vector_store.delete(["01K85F9HDK4H98QK221YA2ZQ7E"])
# print(vector_store.get_by_ids(["01K85F9HDK4H98QK221YA2ZQ7E"]))
#
# # vector_store.index.drop_keys(["qa:01K85F9HDK4H98QK221YA2ZQ7E"])
#
# # 全量删除(连带索引结构全部删除)
# vector_store.index.delete(drop=True)

# 检索
# search_docs = vector_store.similarity_search(query="项目介绍", k=2)
# 结果打分: 分数越低表示相似度越高
# search_docs_results = vector_store.similarity_search_with_score(query="项目介绍", k=2)

# 过滤条件：
# (category == "QA") &  (num > 6)
filter_condition = (Tag("category") == "QA") & (Num("num") > 6)
# search_docs_results = vector_store.similarity_search_with_score(
#     query="项目介绍",
#     k=2,
#     filter=filter_condition
# )

# MMR 搜索： 基于语义搜索，先筛选出一批文档，然后进行重排序输出
search_docs = vector_store.max_marginal_relevance_search(
    query="项目介绍",
    k=2,
    filter=filter_condition,
    fetch_k=10,
)

# vector_store.similarity_search_by_vector()

for doc in search_docs:
    print("*" * 30)
    print(f"文档内容：{doc.page_content}")
    print(f"文档元数据：{doc.metadata}")

# for doc, score in search_docs_results:
#     print("*" * 30)
#     print(f"文档分数：{score}")
#     print(f"文档内容：{doc.page_content}")
#     print(f"文档元数据：{doc.metadata}")

# 文档元数据：{'source': '../Docs/markdown/脚手架级微服务租房平台Q&A.md', 'category': 'QA', 'num': 6}
# 文档元数据：{'source': '../Docs/markdown/脚手架级微服务租房平台Q&A.md', 'category': 'QA', 'num': 7}




















