# 文档加载器（MD）
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

# single 模式，只生成一个大文档
loader = UnstructuredMarkdownLoader("../Docs/markdown/脚手架级微服务租房平台Q&A.md",)
# Document 列表
data = loader.load()

# 定义文本分割器
# text_splitter = CharacterTextSplitter(
#     separator="\n\n",        # 分割符。一般来说，有一个默认的分割符优先级列表：["\n\n", "\n", " "]
#     chunk_size=400,          # 块大小(参考标准，为了保证段落/句子完整，会超出此设定的大小)
#     chunk_overlap=50,        # 块重叠大小
#     length_function=len,     # 测量字符长度的函数
#     is_separator_regex=False,# 是否正则表达式描写分隔符吗？
# )

# tiktoken 分词器
# text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
#     encoding_name="cl100k_base", # cl100k_base 是tiktoken 分词器中的一种编码方式
#     chunk_size=400,              # 块token大小(参考标准，为了保证段落/句子完整，会超出此设定的大小)
#     chunk_overlap=50,            # 块重叠大小
# )

# 强制按照约定的块大小分割文本
# text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#     encoding_name="cl100k_base", # cl100k_base 是tiktoken 分词器中的一种编码方式
#     chunk_size=100,              # 块token大小(参考标准，为了保证段落/句子完整，会超出此设定的大小)
#     chunk_overlap=0,            # 块重叠大小
# )

text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " "],        # 分割符。一般来说，有一个默认的分割符优先级列表：["\n\n", "\n", " "]
    chunk_size=100,          # 块大小(参考标准，为了保证段落/句子完整，会超出此设定的大小)
    chunk_overlap=0,        # 块重叠大小
    length_function=len,     # 测量字符长度的函数
    is_separator_regex=False,# 是否正则表达式描写分隔符吗？
)

# 分割文档
documents = text_splitter.split_documents(data)
for document in documents[:10]:
    print("*" * 30)
    print(document)

# import tiktoken
#
# # 定于cl100k_base编码方式的分词器
# enc = tiktoken.get_encoding("cl100k_base")
#
# # 进行切分编码
# enc_output = enc.encode("my name is LiHua!")
#
# # 打印结果
# print(f"编码后的token：{str(enc_output)}")
# for token in enc_output:
#     print(f"将token: {str(token)} 变成文本:{str(enc.decode_single_token_bytes(token))}")