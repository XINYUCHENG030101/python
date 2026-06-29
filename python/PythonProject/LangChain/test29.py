from langchain_text_splitters import PythonCodeTextSplitter

# 字符串文档
PYTHON_CODE = """
def hello_world():
    print("Hello, World!")

def hello_python():
    print("Hello, Python!")
"""

# 分割器（python代码）
splitter = PythonCodeTextSplitter(
    chunk_size=50,
    chunk_overlap=0,
)

# 创建文档：遵守分割器规则
python_docs =  splitter.create_documents([PYTHON_CODE])

for document in python_docs:
    print("*" * 30)
    print(document)


