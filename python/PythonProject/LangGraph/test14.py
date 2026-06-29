import operator
import uuid
from typing import TypedDict, Annotated, Optional

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, AIMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field



# 准备工作
class Person(BaseModel):
    """一个人的信息"""
    name: Optional[str] = Field(default=None, description="人的姓名")
    height: Optional[str] = Field(default=None, description="以米为单位的身高")
    favourite_food: Optional[list[str]] = Field(default=None, description="最喜欢的食物列表")


search = TavilySearch(max_results=4)
tools = [search]
model = init_chat_model("gpt-4o-mini", temperature=0)
model_with_tools =  model.bind_tools(tools)
model_with_structured = model.with_structured_output(Person)

# 1. 状态定义
class MessagesState(TypedDict):
    # 消息列表
    # 1. 会话记忆
    # 2. 上下文的维护
    messages: Annotated[list[AnyMessage], operator.add]
    # 调用LLM次数
    llm_calls: int


# 2. 节点定义

def get_person_by_llm(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    """通过LLM提取我的信息"""
    # 只要能拿到store，就可以进行持久化存储
    # 需要构造namespace(user_id), 就需要获取config
    people_info = model_with_structured.invoke(
        [
            SystemMessage(content="你是一个提取信息的专家，只从文本中提取我的相关信息，不能提取别人的信息。如果你不知道要提取的属性的值，属性值返回null。")
        ] + state["messages"][-3:]    # 获取最新的三条消息
    )

    # 保存提取出来的用户信息

    user_id = config["configurable"]["user_id"]
    namespace1 = (user_id, "info")
    # put之前应该先查询有没有，再去put（省略）
    store.put(
        namespace1,
        str(uuid.uuid4()),
        {
            "name": people_info.name,
            "height": people_info.height,
        }
    )

    namespace2 = (user_id, "prefs")
    store.put(
        namespace2,
        str(uuid.uuid4()),
        {
            "favourite_food": people_info.favourite_food,   # 直接新增链表（这里是演示，应该追加链表）
        }
    )

    return {
        "llm_calls": state.get("llm_calls", 0) + 1
    }



def llm_call(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    """LLM决定是否调用工具"""

    user_id = config["configurable"]["user_id"]
    namespace1 = (user_id, "info")
    namespace2 = (user_id, "prefs")
    info_result = store.search(namespace1, limit=1)
    prefs_result = store.search(namespace2, limit=1)
    print(info_result)
    print(prefs_result)

    # 由于当前节点有可能是START过来的，也有可能是工具节点过来的，
    # 因此state["messages"]获取的消息：[H]、[H，A，T]
    messages = state["messages"]
    # result可能1：带有tool_calls的AIMessage
    # result可能2：不带tool_calls的AIMessage（最终结果）
    result = model_with_tools.invoke(
        [
            SystemMessage(content="你是一个乐于助人的助手，支持调用工具进行搜索")
        ] + [HumanMessage(content=f"必须参考以下信息："
                          f"1. 用户基本情况：{info_result[0].value}"
                          f"2. 用户偏好情况：{prefs_result[0].value}")]
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
agent_builder.add_node(get_person_by_llm)
agent_builder.add_edge(START, "get_person_by_llm")
agent_builder.add_edge("get_person_by_llm", "llm_call")


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
agent_builder.add_edge("tool_node", "get_person_by_llm")

# 4. 编译图
agent_search = agent_builder.compile(checkpointer=InMemorySaver(), store=InMemoryStore())

# 5. 执行图

# 模拟第一次执行
config1 = {"configurable": {"thread_id": "1111", "user_id": "user_123"}}
result1 = agent_search.invoke({
    "messages": [HumanMessage(content="我叫小明，我喜欢吃川菜里的回锅肉")]
}, config1)
result1["messages"][-1].pretty_print()

# 模拟第二次执行，新开对话
config2 = {"configurable": {"thread_id": "2222", "user_id": "user_123"}}
result2 = agent_search.invoke({
    "messages": [HumanMessage(content="给我推荐一下餐厅")]
}, config2)
for msg in result2["messages"]:
    msg.pretty_print()
