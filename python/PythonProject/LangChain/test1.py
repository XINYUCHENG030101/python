from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

# 1. 定义OpenAI模型
# 默认从系统环境变量中读取 OPENAI_API_KEY
model = ChatOpenAI(model="gpt-4o-mini")

# 2. 定义消息
# 用户消息 HumanMessage
# 系统提示消息 SystemMessage  通常作为第一条消息传入
# AI 消息 AIMessage
messages = [
    SystemMessage(content="请帮我进行翻译，由英文翻译成中文！"),
    HumanMessage(content="my name is xiaoming")
]

# 3. 调用大模型
# result = model.invoke(messages)
# print(result)

# 链式体现在哪里？？？

# 4. 定义输出解析器组件
parser = StrOutputParser()
# print(parser.invoke(result))

# 5. 定义链
# 执行链
chain = model | parser
# chain = RunnableSequence(first=model, last=parser)
# chain = model.pipe(parser)
print(chain.invoke(messages))





