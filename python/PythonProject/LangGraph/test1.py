import operator
from typing import TypedDict, Annotated

from langgraph.constants import START, END
from langgraph.graph import StateGraph


# 1. 状态定义（贯穿整个图）
class PackageState(TypedDict):
    # input: str
    # output: str

    # 包裹状态：
    # 包裹id
    package_id: str
    # 包裹始发站
    origin: str
    # 包裹终点站
    destination: str

    # next: str

    # 配送状态：
    # 状态（“待揽收”、“已揽收”、“运输中”、“派送中”、“已签收”）
    status: str
    # 流转历史 list
    # 知识点：
    # history: list[str]   # 覆盖更新
    history: Annotated[list[str], operator.add]     # 追加更新
    # 总历程
    total_distance: Annotated[int, operator.add]

    # 配送详情:
    # (“普通”，“加急”)
    priority: str

# 2. 节点定义（函数）
# 输入：状态
# 输出：状态的更新
# 节点之前使用state进行通信
# def test(state: PackageState):
#     return {
#         "history": ["揽收站"],
#         "total_distance": 500
#     }

# 揽收站节点
def receive_package(state: PackageState):
    """揽收站"""
    # 进行状态扭转
    # 状态值获取
    print("---执行到揽收站节点")

    origin = state["origin"]
    return {
        "status": "已揽收",
        "history": [f"在{origin}揽收"]
    }

# 分拣中心节点：根据目的地进行分拣
def sort_package(state: PackageState):
    """分拣中心：根据目的地进行分拣"""
    print("---执行到分拣中心节点")

    destination = state["destination"]

    if "北京" in destination:
        next = "北京分拣中心"
    elif "上海" in destination:
        next = "上海分拣中心"
    else:
        next = "其他地区分拣中心"

    return {
        "status": "已分拣",
        "history": [f"分拣至{next}"]
    }

# 派送站节点
def final_delivery(state: PackageState):
    """派送站"""
    return {
        "status": "已签收",
        "history": [f"已送达{state["destination"]}"]
    }

# 标准配送节点
def standard_delivery(state: PackageState):
    """标准配送"""
    return {
        "status": "运输中",
        "history": ["标准陆运"],
        "total_distance": 500
    }

# 加急配送节点
def express_delivery(state: PackageState):
    """加急配送"""
    return {
        "status": "加急运输",
        "history": ["空运加急"],
        "total_distance": 800
    }

# 3. 定义图（依赖状态）
delivery = StateGraph(PackageState)

# 4. 添加节点
delivery.add_node("揽收站", receive_package)
delivery.add_node("分拣中心", sort_package)
delivery.add_node("派送站", final_delivery)
delivery.add_node("标准配送", standard_delivery)
delivery.add_node("加急配送", express_delivery)
# delivery.add_node("不知名节点", test)


# 5. 添加边
delivery.add_edge(START, "揽收站")  # 固定边
delivery.add_edge("揽收站", "分拣中心")

# 路由方法
# def select_delivery(state: PackageState):
#     priority = state["priority"]
#     if priority == "加急":
#         return "加急配送"   # 返回的是字符串，不是节点
#     else:
#         return "标准配送"   # 返回的是字符串，不是节点
#
# # 添加条件边
# delivery.add_conditional_edges(
#     "分拣中心",   # 条件的起始节点
#     select_delivery,   # path：确定下一个节点可调节对象
#     ["加急配送", "标准配送"]  # path_map: 节点名称
# )

def select_delivery(state: PackageState):
    priority = state["priority"]
    if priority == "加急":
        return "备注加急"   # 返回的是字符串，不是节点
    else:
        return "无备注"   # 返回的是字符串，不是节点
# 添加条件边
delivery.add_conditional_edges(
    "分拣中心",   # 条件的起始节点
    select_delivery,   # path：确定下一个节点可调节对象
    {
        "备注加急": "加急配送",
        "无备注": "标准配送"
    }
)
delivery.add_edge("加急配送", "派送站")
delivery.add_edge("标准配送", "派送站")
delivery.add_edge("派送站", END)

# 6. 编译图
delivery_system = delivery.compile()

# 7. 执行图（输入初始状态，输出最终状态）
test_packages = [
    {
        "package_id": "P001",
        "origin": "北京",
        "destination": "上海",
        "priority": "普通",
        "history": [],
        "total_distance": 0
    },
    {
        "package_id": "P002",
        "origin": "广州",
        "destination": "乌鲁木齐",
        "priority": "加急",
        "history": [],
        "total_distance": 0
    }
]

for package in test_packages:
    print(f"\n配送包裹: {package['package_id']}")
    # 执行图，发一遍快递
    result = delivery_system.invoke(package)
    print("最终状态:", result["status"])
    print("配送历史:", result["history"])
    print("总里程:", result["total_distance"])