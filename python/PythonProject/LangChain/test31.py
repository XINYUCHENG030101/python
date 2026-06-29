from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

# 定义嵌入模型
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# 内存向量存储
vector_store = InMemoryVectorStore(embedding=embeddings)

# 获取文档列表
# single 模式，只生成一个大文档
loader = UnstructuredMarkdownLoader("../Docs/markdown/脚手架级微服务租房平台Q&A.md",)
# Document 列表
data = loader.load()

# tiktoken 分词器
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base", # cl100k_base 是tiktoken 分词器中的一种编码方式
    chunk_size=400,              # 块token大小(参考标准，为了保证段落/句子完整，会超出此设定的大小)
    chunk_overlap=50,            # 块重叠大小
)

# 文档列表
docs = text_splitter.split_documents(data)

# 存储文档到内存向量存储中
# add_documents: 将要存储的文档列表进行编排索引。
ids = vector_store.add_documents(docs)
print(f"共有{len(docs)}个文档，编排了{len(ids)}个索引")
print(f"前三个文档的索引：{ids[:3]}")
#
# # 根据索引获取文档
# doc_2 = vector_store.get_by_ids(ids[:2])
# print(doc_2)
#
# # 删除文档
# vector_store.delete(ids=ids[:2])
#
# doc_3 = vector_store.get_by_ids(ids[:3])
# print(doc_3)

# 检索
# similarity_search: 根据余弦相似度来捕捉语义的
# search_docs = vector_store.similarity_search(query="项目介绍", k=2)
# for doc in search_docs:
#     print("*" * 30)
#     print(doc)

# 元数据过滤-》检索
# {'source': '../Docs/markdown/脚手架级微服务租房平台Q&A.md'}
def _filter_function(doc: Document) -> bool:
    return doc.metadata.get("source") == "../Docs/markdown/脚手架级微服务租房平台Q&A.md"

search_docs = vector_store.similarity_search(
    query="项目介绍",
    k=2,
    filter=_filter_function   # filter 接收一个bool值
)

for doc in search_docs:
    print("*" * 30)
    print(doc)










