from langchain_openai import ChatOpenAI
from langsmith import Client

client = Client()
# prompt 就是一个提示词模板 ， Runnable 实例
prompt = client.pull_prompt("hardkothari/prompt-maker", include_model=True)

# 模型
model = ChatOpenAI(model="gpt-4o-mini")

# 链
chain = prompt | model


while True:
    task = input("\n你的任务是什么？ （输入 quit 退出聊天）\n")
    if task == 'quit':
        break

    lazy_prompt = input("\n你当前任务对应的提示词是什么？ （输入 quit 退出聊天）\n")
    if lazy_prompt == 'quit':
        break

    chain.invoke({"task": task, "lazy_prompt": lazy_prompt}).pretty_print()