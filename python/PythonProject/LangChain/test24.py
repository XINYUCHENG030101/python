from langchain_chroma import Chroma
from langchain_core.example_selectors import LengthBasedExampleSelector, SemanticSimilarityExampleSelector, \
    MaxMarginalRelevanceExampleSelector
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_community.example_selectors import NGramOverlapExampleSelector
from langchain_openai import OpenAIEmbeddings

# 反义词示例集合
# examples = [
#     {"input": "happy", "output": "sad"},
#     {"input": "tall", "output": "short"},
#     {"input": "energetic", "output": "lethargic"},
#     {"input": "sunny", "output": "gloomy"},
#     {"input": "windy", "output": "calm"},
# ]

# 示例模板(文本)
example_prompt = PromptTemplate.from_template("Input: {input}\nOutput: {output}")

# # 示例选择器（长度）
# example_selector = LengthBasedExampleSelector(
#     examples=examples,
#     example_prompt=example_prompt,
#     max_length=25,   # 格式化示例的最大长度
#     # 用于获取字符串长度的函数，用于确定包含哪些示例。
#     # 如果没有指定，它是作为默认值提供的。
#     # 该函数返回一个整数，表示字符串中由换行符或空格分隔的“单词”数量
#     # get_text_length: Callable[[str], int] = lambda x: len(re.split("\n| ", x))
# )

# # 示例选择器（语义相似性）
# example_selector = SemanticSimilarityExampleSelector.from_examples(
#     examples,                                         # 示例集
#     OpenAIEmbeddings(model="text-embedding-3-large"), # 使用嵌入模型的能力度量语义
#     Chroma,                                           # 存储向量：向量数据库
#     k=2,                                              # 生成示例的数量
# )

# 示例选择器（MMR）
# example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
#     examples,                                         # 示例集
#     OpenAIEmbeddings(model="text-embedding-3-large"), # 使用嵌入模型的能力度量语义
#     Chroma,                                           # 存储向量：向量数据库
#     k=5,                                              # 生成示例的数量
# )

examples = [
    {"input": "See Spot run.", "output": "看见Spot跑。"},
    {"input": "My dog barks.", "output": "我的狗叫。"},
    {"input": "Spot can run.", "output": "Spot可以跑。"},
]

# 示例选择器（NGram）
example_selector = NGramOverlapExampleSelector(
    examples=examples,
    example_prompt=example_prompt,
    threshold=1.0,  # 阈值.
                    # 负值代表不相干的示例也被筛选出来
                    # 0.0，输出结果是只与输入重叠的示例
                    # 大于等于1.0，排除所有示例，返回空列表
)

few_shot_prompt = FewShotPromptTemplate(
    example_selector=example_selector,   # 示例选择器
    example_prompt=example_prompt,
    prefix="给出每个输入的中文翻译：",
    suffix="Input: {sentence}\nOutput: ",
    input_variables=["sentence"],
)

# 少样本模板
# 转换 Message
# few_shot_prompt = FewShotPromptTemplate(
#     example_selector=example_selector,   # 示例选择器
#     example_prompt=example_prompt,
#     prefix="给出每个输入的反义词：",
#     suffix="Input: {adjective}\nOutput: ",
#     input_variables=["adjective"],
# )


print(
    few_shot_prompt.invoke({"sentence": "Spot can run fast."}).to_messages()[0].content
)

