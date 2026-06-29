from typing import TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.constants import START
from langgraph.graph import StateGraph

model = init_chat_model("gpt-4o-mini")

class InputState(TypedDict):
    topic: str      # 主题

class OutputState(TypedDict):
    final_content: str   # 文章

# 过程中状态模式（内部使用）
class State(InputState, OutputState):
    outline: str  # 第一步：生成的大纲
    draft: str  # 第二步：生成的初稿
    polished_draft: str  # 第三步：润色后的稿件


# 节点一
PROMPT_1 = (
    "根据主题生成文章大纲。\n"
    "主题：{topic}\n"
    "要求："
    "1.只需两个最核心标题"
    "2.不用进行说明，只返回最终大纲"
)
def node_1(state: InputState):
    """根据主题生成内容大纲"""

    print("*" * 50)
    print(f"内容大纲生成中...\n")
    prompt = PROMPT_1.format(topic=state["topic"])
    result = model.invoke([HumanMessage(content=prompt)])
    print(f"大纲已生成：\n{result.content}\n")
    return {
        "outline": result.content
    }

# 节点二
PROMPT_2 = (
    "根据以下内容生成文章完整初稿。\n"
    "主题：{topic}\n"
    "大纲: "
    "{outline}\n"
    "要求："
    "1.每个标题下，最多使用三句话的内容即可"
    "2.不用进行说明，只返回最终结果"
)
def node_2(state: State):
    """根据内容大纲生成初稿"""

    print("*" * 50)
    print(f"初稿生成中...\n")
    prompt = PROMPT_2.format(topic=state["topic"], outline=state["outline"])
    result = model.invoke([HumanMessage(content=prompt)])
    print(f"初稿已生成：\n{result.content}\n")
    return {
        "draft": result.content
    }

# 节点三
PROMPT_3 = (
    "根据文章初稿进行润色。\n"
    "主题：{topic}\n"
    "初稿: "
    "{draft}\n"
    "要求："
    "1.润色后，文章不能太长"
)
def node_3(state: State):
    """润色初稿"""

    print("*" * 50)
    print(f"初稿润色中...\n")
    prompt = PROMPT_3.format(topic=state["topic"], draft=state["draft"])
    result = model.invoke([HumanMessage(content=prompt)])
    print(f"初稿润色完成：\n{result.content}\n")
    return {
        "polished_draft": result.content
    }


# 节点四
PROMPT_4 = (
    "根据润色版文章，生成文章终稿。\n"
    "主题：{topic}\n"
    "大纲: "
    "{outline}\n"
    "润色版文章: "
    "{polished_draft}\n"
)
def node_4(state: State):
    """生成终稿"""

    print("*" * 50)
    print(f"终稿生成中...\n")
    prompt = PROMPT_4.format(topic=state["topic"], outline=state["outline"], polished_draft=state["polished_draft"])
    result = model.invoke([HumanMessage(content=prompt)])
    print(f"终稿已完成：\n{result.content}\n")
    return {
        "final_content": result.content
    }

builder = StateGraph(
    State,
    input_schema=InputState,  # 输入验证
    output_schema=OutputState # 输出过滤
)
builder.add_sequence([node_1, node_2, node_3, node_4])
builder.add_edge(START, "node_1")
chain = builder.compile()
result = chain.invoke({"topic": "人工智能的未来发展"})
print(result)
