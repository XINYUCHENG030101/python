import operator
from typing import TypedDict, Annotated

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import Send
from pydantic import BaseModel


# 状态定义
class State(TypedDict):
    topic: str      # 任务主题
    sections: list  # 协调者生成的子任务清单
    completed_sections: Annotated[list, operator.add]   # 工作者完成的结果列表
    final_report: str  # 整合器的产出结果

# 一个章节的内容
class Section(BaseModel):
    name: str
    description: str

# 完整章节
class Sections(BaseModel):
    sections: list[Section]

model = init_chat_model("gpt-4o-mini")
planner = model.with_structured_output(Sections)

# 协调者节点
def orchestrator(state: State):
    """协调者：分析任务并制定计划"""
    print("协调者进行任务拆分...")
    result = planner.invoke(
        [HumanMessage(content=f"为主题{state["topic"]}制定报告大纲，要包含三到五个章节，具体个数你自己定，但要在个数要求内")]
    )
    return {
        "sections": result.sections
    }

# 工作者节点
def worker_1(state: State):
    """工作者：根据分配的章节生成内容"""

    print("工作者正在生成内容...")

    # 不对的，具体的工作者不知道要完成哪个任务
    # sections = state["sections"]

    # state["section"] 就是通过 Send 对象传递过来的状态
    section = state["section"]

    result = model.invoke([
        HumanMessage(content=f"编写报告章节：{section.name}, 内容要求：{section.description}")
    ])
    return {
        "completed_sections": [result.content]  # 合并工作者结果
    }


# 汇总节点
def synthesizer(state: State):
    """汇总所有工作者的结果"""
    print("正在汇总内容...")
    completed_sections = state["completed_sections"]
    final_report = "\n\n ---- \n\n".join(completed_sections)
    return {
        "final_report": final_report
    }

builder = StateGraph(State)
builder.add_node(orchestrator)
builder.add_node(worker_1)
builder.add_node(synthesizer)

builder.add_edge(START, "orchestrator")

def assign_workers(state: State):
    """为每个任务（章节）分配工作者"""
    worker_tasks = []
    for section in state["sections"]:
        # 分配（在运行时确定要执行哪个工作节点）
        # 节点间是依靠状态进行通信的，
        # 因此在这里我们需要拿到下一个工作节点的名称，
        # 以及要传递给这个节点的状态（具体哪个任务）

        # # 要知道有哪些备选池中的工作节点
        # if xxxx:
        #     Send("worker_1", {"section": section})
        # if xxxx:
        #     Send("worker_2", {"section": section})

        worker_tasks.append(
            Send("worker_1", {"section": section})  # Send是一个对象：1. 节点名称  2. 发送给节点的状态
        )

    return worker_tasks  # Send对象列表，被条件边接收，用来让条件边再运行时判断后续节点是谁
    # return "node1"  # 返回固定路径

# 对条件边来说，除了返回固定的节点外，也可以接收Send对象列表(运行时确定后续节点)
builder.add_conditional_edges(
    "orchestrator",
    assign_workers,
    # 构建图时，不知道后续会走哪个节点
    # ["worker_1"]
)
builder.add_edge("worker_1", "synthesizer")
builder.add_edge("synthesizer", END)
worker = builder.compile()
# print(worker.get_graph(xray=True).draw_mermaid())

worker.invoke({
    "topic": "中国近代史"
})