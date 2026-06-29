from langchain_core.prompts import FewShotChatMessagePromptTemplate, FewShotPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI


model = ChatOpenAI(model="gpt-4o-mini")

# 文本提示词模板
example_prompt = PromptTemplate.from_template("Question: {question}\n{answer}")

# 创建示例集
examples = [
    {
        "question": "李白和杜甫，谁更长寿？",
        "answer": """
        是否需要后续问题：是的。
        后续问题：李白享年多少岁？
        中间答案：李白享年61岁。
        后续问题：杜甫享年多少岁？
        中间答案：杜甫享年58岁。
        所以最终答案是：李白
        """
    },
    {
        "question": "腾讯的创始人什么时候出生？",
        "answer": """
        是否需要后续问题：是的。
        后续问题：腾讯的创始人是谁？
        中间答案：腾讯由马化腾创立。
        后续问题：马化腾什么时候出生？
        中间答案：马化腾出生于1971年10月29日。
        所以最终答案是：1971年10月29日
        """,
    },
    {
        "question": "孙中山的外祖父是谁？",
        "answer": """
        是否需要后续问题：是的。
        后续问题：孙中山的母亲是谁？
        中间答案：孙中山的母亲是杨太夫人。
        后续问题：杨太夫人的父亲是谁？
        中间答案：杨太夫人的父亲是杨胜辉。
        所以最终答案是：杨胜辉
        """,
    },
    {
        "question": "电影《红高粱》和《霸王别姬》的导演来自同一个国家吗？",
        "answer": """
        是否需要后续问题：是的。
        后续问题：《红高粱》的导演是谁？
        中间答案：《红高粱》的导演是张艺谋。
        后续问题：张艺来自哪里？
        中间答案：中国。
        后续问题：《霸王别姬》的导演是谁？
        中间答案：《霸王别姬》的导演是陈凯歌。
        后续问题：陈凯歌来自哪里？
        中间答案：中国。
        所以最终答案是：是
        """,
    },
]

# 消息通过提示词模板构建出来
# FewShotPromptTemplate 针对文本、消息
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,  # PromptTemplate，用于格式化单个示例
    suffix="Question: {input}",     # suffix表示放在示例之后的模板字符串
    input_variables=["input"],      # 输入变量列表
)
# print(few_shot_prompt.invoke({"input": "《教父》和《星球大战》的导演是否来自一个国家？"}).to_string())
# print(few_shot_prompt.invoke({"input": "《教父》和《星球大战》的导演是否来自一个国家？"}).to_messages())


chain = few_shot_prompt | model
chain.invoke({"input": "《教父》和《星球大战》的导演是否来自一个国家？"}).pretty_print()