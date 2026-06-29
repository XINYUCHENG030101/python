import operator
from typing import TypedDict, Annotated

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, AIMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_tavily import TavilySearch
from langgraph.constants import START, END
from langgraph.graph import StateGraph

# 准备工作
search = TavilySearch(max_results=4)
tools = [search]
model = init_chat_model("gpt-4o-mini", temperature=0)
model_with_tools =  model.bind_tools(tools)

# 1. 状态定义
class MessagesState(TypedDict):
    # 消息列表
    # 1. 会话记忆
    # 2. 上下文的维护
    messages: Annotated[list[AnyMessage], operator.add]
    # 调用LLM次数
    llm_calls: int

# def node(state: MessagesState):
#     messages = state["messages"]
#     result = llm.invoke(messages)
#     state["messages"][-1]
#     new_message = AIMessage(content="i am ai")
#     return {
#         "messages": [new_message]
#     }

# 2. 节点定义
def llm_call(state: MessagesState):
    """LLM决定是否调用工具"""

    # 由于当前节点有可能是START过来的，也有可能是工具节点过来的，
    # 因此state["messages"]获取的消息：[H]、[H，A，T]
    messages = state["messages"]
    # result可能1：带有tool_calls的AIMessage
    # result可能2：不带tool_calls的AIMessage（最终结果）
    result = model_with_tools.invoke(
        [
            SystemMessage(content="你是一个乐于助人的助手，支持调用工具进行搜索")
        ]
        + messages
    )
    return {
        "messages" : [result],
        "llm_calls": state.get("llm_calls", 0) + 1   # 覆盖更新
    }

tools_by_name = {tool.name: tool for tool in tools}
def tool_node(state: MessagesState):
    """执行工具调用"""
    # result 就是 ToolMessage

    result = []
    # 当前最新的消息就是带有tool_calls的AImessage
    for tool_call in state["messages"][-1].tool_calls:
        # 就可以获取到tool_call的name,args,id...
        # 要根据tool_call知道，去执行哪个工具
        tool = tools_by_name[tool_call["name"]]
        obs = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=obs, tool_call_id=tool_call["id"]))

    return {
        "messages": result,
    }

# 3. 定义图，添加节点和边
agent_builder = StateGraph(MessagesState)
agent_builder.add_node(llm_call)
agent_builder.add_node(tool_node)

agent_builder.add_edge(START, "llm_call")

def should_continue(state: MessagesState):
    # 最新消息是AIMessage，要判断它是否带有tool_calls
    # 带有tool_calls：要走tool_node
    # 不带：END

    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool_node"

    return END

agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

# 4. 编译图
agent_search = agent_builder.compile()

# 5. 生成图样式
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# try:
#     # 生成 Mermaid 图表并保存为图片
#     mermaid_code = agent_search.get_graph(xray=True).draw_mermaid()
#     print(mermaid_code)
#     # # 保存文件
#     # with open("../jpg/graph2.jpg", "wb") as f:
#     #     f.write(mermaid_code)
#     #
#     # # 使用 matplotlib 显示图像
#     # img = mpimg.imread("../jpg/graph2.jpg")
#     # plt.imshow(img)  # 显示图片
#     # plt.axis('off')  # 关闭坐标轴
#     # plt.show()  # 弹出窗口显示图片
# except Exception as e:
#     print(f"An error occurred: {e}")


# 6. 执行图
result = agent_search.invoke({
    # "messages": [HumanMessage(content="今天西安的天气如何？")]
    "messages": [HumanMessage(content="你好")]
})
# result 是最终的状态结果
print(f"一共调用了{result["llm_calls"]}次LLM")
for msg in result["messages"]:
    msg.pretty_print()
