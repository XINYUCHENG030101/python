from typing import Iterator, List

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 组件1：聊天模型
model = ChatOpenAI(model="gpt-4o-mini")
# 组件2：输出解析器（str）
parser = StrOutputParser()

# 自定义生成器
def split_into_list(input: Iterator[str]) -> Iterator[List[str]]:
    buffer = ""
    for chunk in input:
        buffer += chunk
        # 遇到 。 需要刷新
        while "。" in buffer:
            # 找到 。的位置
            stop_index = buffer.index("。")
            # yield 用于创造生成器
            yield [buffer[:stop_index].strip()]
            buffer = buffer[stop_index + 1 :]
    # 处理buffer最后几个字
    yield [buffer.strip()]


# 定义链
chain = model | parser | split_into_list

# 返回一个迭代器，产生的消息块
for chunk in chain.stream("写一段关于爱情的歌词，需要5句话，每句话用中文句号隔开。"):
    # chunk: AIMessageChunk
    # print(chunk.content, end="|", flush=True)
    # 使用 parser，结果就是 str
    print(chunk, end="|", flush=True)

# tmp_chunks = chunks[0] + chunks[1] + chunks[2] +chunks[3]
# print(tmp_chunks)