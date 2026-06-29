import asyncio
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini")

# 返回一个迭代器，产生的消息块
# chunks = []
# for chunk in model.stream("写一段关于春天的作文，1000字"):
#     chunks.append(chunk)
#     # chunk: AIMessageChunk
#     print(chunk.content, end="|", flush=True)

# tmp_chunks = chunks[0] + chunks[1] + chunks[2] +chunks[3]
# print(tmp_chunks)

# print(model.invoke("写一段关于春天的作文，1000字").content)


# 异步流式输出
async def async_stream():
    print("===异步调用===")
    async for chunk in model.astream("写一段关于春天的作文，1000字"):
        print(chunk.content, end="|", flush=True)

asyncio.run(async_stream())

# model.ainvoke()