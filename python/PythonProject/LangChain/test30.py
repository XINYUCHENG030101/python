from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

# 定义嵌入模型
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
)

#######################################query表示向量#################################################


# 将query转换成向量表示
query_vector = embeddings.embed_query("你好")
# print(f"text-embedding-3-large 向量维度：{len(query_vector)}")
# print(f"向量前五个数值：{query_vector[:5]}")

#######################################文档表示向量#################################################

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

# 将文档列表表示为向量列表
# 参数：texts: list[str]
texts = [doc.page_content for doc in docs]
docs_vector = embeddings.embed_documents(texts)

print(f"文档数量：{len(docs)}，转换的向量列表数量：{len(docs_vector)}")
print(f"第一个文档向量维度：{len(docs_vector[0])}")
print(f"第一个文档向量前五个值：{docs_vector[0][:5]}")



