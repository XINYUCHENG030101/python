from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import CharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec

# 创建Pinecone客户端
pc = Pinecone()
index_name = "qa"
if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=3072,   # 维度
        metric="cosine",  # 度量方式，cosine余弦相似度
        spec=ServerlessSpec(
            cloud="aws",               # 亚马逊云
            region="us-east-1"         # 区域
        ),
    )

# 获取索引
index = pc.Index(index_name)
# 嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# 定义 pinecone 向量库
vector_store = PineconeVectorStore(
    embedding=embeddings,
    index=index,          # pinecone 向量库的索引
)


# # single 模式，只生成一个大文档
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
#
# # 添加文档
# ids = vector_store.add_documents(documents=docs)
# print(f"编制了{len(ids)}个索引")
# print(f"前三个索引是：{ids[:3]}")

# # 全量删除
# vector_store.delete(delete_all=True)
#
# # 删除指定id的文档列表
# delete_ids = []
# vector_store.delete(ids=delete_ids)

# 搜索文档
search_docs = vector_store.similarity_search(query="项目介绍", k=2)
for doc in search_docs:
    print("*" * 30)
    print(f"文档内容：{doc.page_content}")
    print(f"文档元数据：{doc.metadata}")