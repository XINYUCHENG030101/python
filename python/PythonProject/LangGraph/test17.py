from typing import TypedDict, Optional, Literal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class ApprovalState(TypedDict):
    action_details: str        # 操作详情（如"转账30000元"）
    status: Optional[Literal["等待", "批准", "拒绝"]]   # 审批状态

# 1. 保存审批状态，由条件边决定后续流程
# def approval_node(state:ApprovalState):
#     decision = interrupt({
#         "question": "是否批准此操作？",
#         "details": state["action_details"],
#         "ops": "请输入【批准】或【拒绝】"
#     })
#
#     return {
#         "status": decision
#     }

# 2. 节点中，直接判断后续执行流程
def approval_node(state: ApprovalState):
    decision = interrupt({
        "question": "是否批准此操作？",
        "details": state["action_details"],
        "ops": "请输入【批准】或【拒绝】"
    })
    if decision == "批准":
        next_node = "proceed_node"
    else:
        next_node = "cancel_node"

    return Command(goto=next_node)

def proceed_node(state:ApprovalState):
    print("批准")
    return {"status": "批准"}

def cancel_node(state:ApprovalState):
    print("取消")
    return {"status": "取消"}

builder = StateGraph(ApprovalState)
builder.add_node(approval_node)
builder.add_node(proceed_node)
builder.add_node(cancel_node)
builder.add_edge(START, "approval_node")

# def approval(state:ApprovalState):
#     if state["status"] == "批准":
#         return "proceed_node"
#     else:
#         return "cancel_node"
#
# # 条件边：根据人工审核结果决定后续流程
# builder.add_conditional_edges(
#     "approval_node",
#     approval,
#     ["proceed_node", "cancel_node"]
# )
builder.add_edge("proceed_node", END)
builder.add_edge("cancel_node", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "1"}}
print(graph.invoke({"action_details": "转账30000元", "status": "等待"}, config=config))

print(graph.invoke(Command(resume="批准"), config=config))
