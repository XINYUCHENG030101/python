from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langgraph.types import interrupt, Command


@tool
def send_email(to: str, subject: str, body: str):
    """发送电子邮件给收件人"""

    result = interrupt({
        "action": "发送邮件",
        "to": to,
        "subject": subject,
        "body": body,
        "message": "同意发送这封邮件吗？"
    })

    if result["action"] == "不同意":
        return "用户取消发送邮件"

    final_to = result.get("to", to)
    final_subject = result.get("subject", subject)
    final_body = result.get("body", body)
    email_info = f"收件人：{final_to}，主题：{final_subject}， 正文：{final_body}"
    print(f"【发送邮件】{email_info}")
    return email_info

model_with_tool = init_chat_model("gpt-4o-mini").bind_tools([send_email])
def llm_call(state: MessagesState):

    # H、A(tool_call)、T

    # 1. LLM 决定是否调用工具
    result = model_with_tool.invoke(
        [SystemMessage(content="你支持调用工具去发送邮件。")]
        + state["messages"]
    )

    # 2. 执行工具
    if result.tool_calls:
        tool_call = result.tool_calls[0]
        tool_result = send_email.invoke(tool_call["args"])
        return {"messages": [result] + [ToolMessage(content=tool_result, tool_call_id=tool_call["id"])]}

    return {"messages": [result]}

builder = StateGraph(MessagesState)
builder.add_node(llm_call)
builder.add_edge(START, "llm_call")
builder.add_edge("llm_call", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "1"}}
result1 = graph.invoke({"messages": [HumanMessage(content="发送电子邮件至alice@example.com，主题是：请假，内容是：回老家")]},
                       config=config)
print(result1["__interrupt__"])

result2 = graph.invoke(Command(resume={
    "action": "不同意",
    "subject": "请病假"
}), config=config)
result2["messages"][-1].pretty_print()

# Command(resume={
#     "action": "同意",
# })
#
# Command(resume={
#     "action": "不同意",
# })
#
# Command(resume={
#     "action": "同意，需要修改收件人",
#     "to": "张三",
# })
#
# Command(resume={
#     "action": "同意，需要修改主题",
#     "subject": "修改后的主题...",
# })
#
# Command(resume={
#     "action": "同意，需要修改内容",
#     "subject": "修改后的body...",
# })
#
