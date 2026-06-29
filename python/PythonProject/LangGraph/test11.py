import operator
from typing import TypedDict, Annotated

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, AIMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
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

# 4. 编译图(带有内存存储)
# # 定义了一个内存存储库
# checkpointer = InMemorySaver()

# 定义了一个postgres存储库
DB_URI = "postgresql://postgres:bit@192.168.100.233:5432/postgres"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:  # checkpointer 是一个链接好存储库

    # 第一次使用postgres存储库需要执行一下.setup()
    # checkpointer.setup()
    agent_search = agent_builder.compile(checkpointer=checkpointer)

    # 6. 执行图
    # 通过配置的方式将线程id传递给单次执行中
    config = {"configurable": {"thread_id": "2222"}}
    # 模拟第一次执行
    # result = agent_search.invoke(
    #     {"messages": [HumanMessage(content="今天西安的天气如何？")]},
    #     config=config
    # )
    # # result 是最终的状态结果
    # result["messages"][-1].pretty_print()

    # 第二次执行
    # result = agent_search.invoke({
    #     "messages": [HumanMessage(content="刚才我们聊了什么？")]
    # }, config=config)
    # # result 是最终的状态结果
    # for r in result["messages"]:
    #     r.pretty_print()

    # 获取一下最新的状态快照
    # print(agent_search.get_state(config))

    # 历史快照：顺序按照时间排序，最新的在最前面
    # print(list(agent_search.get_state_history(config)))

    to_replay = None
    new_config = None
    for snapshot in agent_search.get_state_history(config):
        # print("checkpointer_id: ", snapshot.config["configurable"]["checkpoint_id"])
        # print("下一个节点：", snapshot.next)
        # print("\n")
        if snapshot.config["configurable"]["checkpoint_id"] == "1f0f75d0-15af-6819-8005-5329d06cd836":
            # print("state: ", snapshot.values["messages"][-1])
            new_config = agent_search.update_state(
                snapshot.config,
                {"messages": [HumanMessage(content="我们之前聊过宠物相关的话题吗？")]}
            )
            print(new_config)
            to_replay = snapshot

    # 重放（从指定的快照开始执行）
    # 参数1：state设置为None，因为重放可以从快照中获取state
    # 参数2：要重放的config，里面包含了线程id，快照id
    result2 = agent_search.invoke(None, config=new_config)
    print(result2["messages"][-1])
# {'messages': [
#     HumanMessage(content='今天西安的天气如何？', additional_kwargs={}, response_metadata={}),
#     AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 23, 'prompt_tokens': 1291, 'total_tokens': 1314, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': None}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_8bbc38b4db', 'id': 'chatcmpl-D0ffm3Kqvhbna8w1HMsGzTPNk7M7w', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--d4906507-5f8d-429f-bfad-efd42648d635-0', tool_calls=[{'name': 'tavily_search', 'args': {'query': '西安天气', 'search_depth': 'basic'}, 'id': 'call_YPHW71KBFGRl3IVMMT1cimxo', 'type': 'tool_call'}], usage_metadata={'input_tokens': 1291, 'output_tokens': 23, 'total_tokens': 1314, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}),
#     ToolMessage(content="{'query': '西安天气', 'response_time': 0.65, 'follow_up_questions': None, 'answer': None, 'images': [], 'results': [{'url': 'https://www.weather.com.cn/weather/101110101.shtml', 'title': '西安天气预报,西安7天天气预报,西安15天天气预报,西安天气查询', 'content': '*   [商洛 _/_ _10/-2°C_](http://www.weather.com.cn/weather1d/101110601.shtml#around2). *   [泾阳 _/_ _11/-3°C_](http://www.weather.com.cn/weather1d/101110205.shtml#around2). *   [渭南 _/_ _11/0°C_](http://www.weather.com.cn/weather1d/101110501.shtml#around2). *   [安康 _/_ _12/-2°C_](http://www.weather.com.cn/weather1d/101110701.shtml#around2). *   [潼关 _/_ _10/-3°C_](http://www.weather.com.cn/weather1d/101110503.shtml#around2). *   [宝鸡 _/_ _9/-3°C_](http://www.weather.com.cn/weather1d/101110901.shtml#around2). *   [铜川 _/_ _4/-7°C_](http://www.weather.com.cn/weather1d/101111001.shtml#around2). *   [长安 _/_ _9/-1°C_](http://www.weather.com.cn/weather1d/101110102.shtml#around2). *   [三原 _/_ _11/-3°C_](http://www.weather.com.cn/weather1d/101110201.shtml#around2). *   [蓝田 _/_ _9/-4°C_](http://www.weather.com.cn/weather1d/101110104.shtml#around2). *   [礼泉 _/_ _11/-2°C_](http://www.weather.com.cn/weather1d/101110202.shtml#around2). *   [临潼 _/_ _10/-1°C_](http://www.weather.com.cn/weather1d/101110103.shtml#around2). *   [水陆庵 _/_ _11/-1°C_](http://www.weather.com.cn/weather1d/10111010401A.shtml#around2). *   [临潼博物馆 _/_ _11/0°C_](http://www.weather.com.cn/weather1d/10111010106A.shtml#around2). *   [陕西自然博物馆 _/_ _11/1°C_](http://www.weather.com.cn/weather1d/10111010107A.shtml#around2). *   [翠华山 _/_ _9/-1°C_](http://www.weather.com.cn/weather1d/10111010108A.shtml#around2). *   [大唐西市文化景区 _/_ _11/2°C_](http://www.weather.com.cn/weather1d/10111010109A.shtml#around2). *   [骊山国家森林公园 _/_ _10/0°C_](http://www.weather.com.cn/weather1d/10111010110A.shtml#around2). *   [曲江海洋公园 _/_ _12/0°C_](http://www.weather.com.cn/weather1d/10111010111A.shtml#around2). *   [陕西历史博物馆 _/_ _11/1°C_](http://www.weather.com.cn/weather1d/10111010112A.shtml#around2). *   [常宁宫休闲山庄 _/_ _11/-1°C_](http://www.weather.com.cn/weather1d/10111010102A.shtml#around2). *   [大兴善寺 _/_ _11/1°C_](http://www.weather.com.cn/weather1d/10111010103A.shtml#around2). *   [沣峪荘园 _/_ _6/-5°C_](http://www.weather.com.cn/weather1d/10111010104A.shtml#around2). *   [广仁寺 _/_ _12/2°C_](http://www.weather.com.cn/weather1d/10111010105A.shtml#around2). [重大天气事件](http://www.weather.com.cn/index/jqzdtqsj/index.shtml). [](http://www.weather.com.cn/index/jqzdtqsj/index.shtml). *   [1月9日 ![Image 23: 未来三天东北降雪明显增强局地或现暴雪 中东部多地气温震荡回升](http://i.weather.com.cn/images/cn/news/2026/01/08/348D4FBCA09F39A6B43010C719C2A75A.jpg)东北地区降雪增强局地或现暴雪 三九期间全国大部偏暖温差增大 ----------------------------- 今天（1月9日），受冷空气影响，东北地区降雪增强，局地将迎暴雪；而全国其他大部地区仍将持续干燥格局。](http://www.weather.com.cn/index/2026/01/4465762.shtml). *   [1月8日 ![Image 24: 未来三天东北降雪明显增强局地或现暴雪 中东部多地气温震荡回升](http://i.weather.com.cn/images/cn/news/2026/01/08/348D4FBCA09F39A6B43010C719C2A75A.jpg)未来三天东北降雪明显增强局地或现暴雪 中东部多地气温震荡回升 ------------------------------ 未来三天（1月8日至10日），受新一股冷空气影响，东北地区的降雪将明显增强，明天是降雪最强时段，局地或现暴雪。](http://www.weather.com.cn/index/2026/01/4464364.shtml). *   [1月6日 ![Image 26: 两股冷空气难阻中东部回暖 雨雪稀少天气持续干燥](http://i.weather.com.cn/images/cn/news/2026/01/06/5AAC1E2FC5B449B693E3EF5984046EB4.JPG)两股冷空气难阻中东部回暖 雨雪稀少天气持续干燥 ----------------------- 今天（1月6日）至周末，将有两股冷空气接连来袭，但由于强度较弱，且影响区域偏北，中东部大部地区将持续回暖，但昼夜温差较大。](http://www.weather.com.cn/index/2026/01/4461872.shtml). [查看更多>>](http://www.weather.com.cn/index/jqzdtqsj/index.shtml). [联播天气预报](http://www.weather.com.cn/video/ylist.shtml). [](http://www.weather.com.cn/video/ylist.shtml). [](http://www.weather.com.cn/video/index.shtml). *   [湖北神农架晨雾缭绕 秋色迷人](http://www.weather.com.cn/life/2019/10/3253317.shtml). *   [换个视角看秋景 竟然这么美！](http://www.weather.com.cn/life/2018/11/2957048.shtml). *   [三亚 多云 25/15℃适宜](http://www.weather.com.cn/weather1d/101310201.shtml). *   [九寨沟 晴转阴 11/-4℃适宜](http://www.weather.com.cn/weather1d/101271906.shtml). *   [大理 多云 15/0℃适宜](http://www.weather.com.cn/weather1d/101290201.shtml). *   [张家界 晴转多云 19/1℃适宜](http://www.weather.com.cn/weather1d/101251101.shtml). *   [桂林 晴转多云 20/3℃适宜](http://www.weather.com.cn/weather1d/101300501.shtml). *   [青岛 晴 8/3℃一般](http://www.weather.com.cn/weather1d/101120201.shtml).', 'score': 0.81595254, 'raw_content': None}, {'url': 'https://www.weather.com.cn/weather40d/101110101.shtml', 'title': '【西安天气】西安40天天气预报,西安更长预报,西安天气日历,西安日历 ...', 'content': '首页 预报 预警 雷达 云图 天气地图 专业产品 资讯 视频 节气 我的天空. 台风路径 空间天气 图片 专题 环境 旅游 碳中和 气象科普 一带一路 产创平台. :   北京 上海 成都 杭州 南京 天津 深圳 重庆 西安 广州 青岛 武汉. :   故宫 阳朔漓江 龙门石窟 野三坡 颐和园 九寨沟 东方明珠 凤凰古城 秦始皇陵 桃花源. :   佘山 春城湖畔 华彬庄园 观澜湖 依必朗 旭宝 博鳌 玉龙雪山 番禺南沙 东方明珠. :   曼谷 东京 首尔 吉隆坡 新加坡 巴黎 罗马 伦敦 雅典 柏林 纽约 温哥华 墨西哥城 哈瓦那 圣何塞 巴西利亚 布宜诺斯艾利斯 圣地亚哥 利马 基多 悉尼 墨尔本 惠灵顿 奥克兰 苏瓦 开罗 内罗毕 开普敦 维多利亚 拉巴特. :   亚洲 欧洲 北美洲 南美洲 非洲 大洋洲. ### 蓝天预报综合天气现象、能见度、空气质量等因子，预测未来一周的天空状况。. :   大风蓝色预警：华北北部等部分地区阵风可达8至10级  中国天气网 2026-01-10 18:05. :   周末山东大风降温齐至 烟台威海等地将有降雪局部暴雪  中国天气网 2026-01-10 11:13. :   辽宁本周末大风寒潮天气来袭阵风可达9级 部分地区仍有降雪  中国天气网 2026-01-10 10:23. :   北京今天风大天寒 最高气温将降至1℃  中国天气网 2026-01-10 07:05. :   大风蓝色预警：内蒙古山东辽宁等地部分地区阵风可达7至9级  中国天气网 2026-01-10 06:05. # 高清图集. # 更多>>高清图集. * 三亚 多云 14/27℃ 适宜. * 九寨沟 晴转阴 -2/10℃ 适宜. * 大理 多云 0/15℃ 适宜. * 张家界 晴 1/15℃ 适宜. * 桂林 多云转晴 8/20℃ 适宜. * 青岛 晴 -3/3℃ 较不宜.', 'score': 0.7587435, 'raw_content': None}, {'url': 'https://tianqi.so.com/weather/101110101', 'title': '【西安天气预报】西安天气预报7天,10天,15天_全国天气网', 'content': '# 全国天气网. 当前时间：2026-01-20周二12:40. 西安市气象台2026年01月19日18时00分继续发布道路结冰黄色预警信号：预计今天晚上到明天白天新城区、碑林区、莲湖区、雁塔区、灞桥区、未央区、阎良区、临潼区、长安区、高陵区、鄠邑区、周至县、蓝田县、西咸新区可能出现对交通有影响的道路结冰，请注意防范。. 西安市气象台2026年01月19日18时00分继续发布道路结冰黄色预警信号：预计今天晚上到明天白天新城区、碑林区、莲湖区、雁塔区、灞桥区、未央区、阎良区、临潼区、长安区、高陵区、鄠邑区、周至县、蓝田县、西咸新区可能出现对交通有影响的道路结冰，请注意防范。. ### 当前天气信息. ### 空气质量. ### 主要污染物. ### 明日天气信息. ### 最优空气质量排行榜. ### 最差空气质量排行榜. 天气冷，建议着棉服、羽绒服、皮夹克加羊毛衫等冬季服装。年老体弱者宜着厚棉衣... 紫外线强度较弱，建议出门前涂擦SPF在12-15之间、PA+的防晒护肤品。. 天气冷，建议着棉服、羽绒服、皮夹克加羊毛衫等冬季服装。年老体弱者宜着厚棉衣... 紫外线强度较弱，建议出门前涂擦SPF在12-15之间、PA+的防晒护肤品。. 2020年6月10日(周三)起，工作日早7:30-9:00，晚18:00-... ### 全国天气. ### 景点天气. ### 国际天气.', 'score': 0.72629017, 'raw_content': None}, {'url': 'http://www.sn.xinhuanet.com/20260122/f9570f28ab9b4223a0c534c61656b85c/c.html', 'title': '西安市气温逐渐回升25日有弱雨雪天气 - 新华网', 'content': '22日至24日西安市将以晴到多云天气为主，最低气温维持在-5℃～-3℃，最高气温逐步回升至7℃，市民可趁晴好天气适度户外活动。 根据市气象台21日预报，22日至24', 'score': 0.72348577, 'raw_content': None}], 'request_id': 'bf0d52ad-566a-4f6c-9114-48dfd18d4593'}", tool_call_id='call_YPHW71KBFGRl3IVMMT1cimxo'),
#     AIMessage(content='今天西安的天气情况如下：\n\n- **气温**：最高气温约为11°C，最低气温约为-3°C。\n- **天气状况**：整体天气较为寒冷，建议穿着保暖的衣物。\n\n如果想要获取更详细的天气信息，可以查看[这里](https://www.weather.com.cn/weather/101110101.shtml)。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 82, 'prompt_tokens': 4515, 'total_tokens': 4597, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': None}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_29330a9688', 'id': 'chatcmpl-D0ffqzEaoyJ09GuLY52h9eHXnxzL5', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--3da222aa-0ab5-415a-9de3-13dd5423110f-0', usage_metadata={'input_tokens': 4515, 'output_tokens': 82, 'total_tokens': 4597, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}),
#     HumanMessage(content='刚才我们聊了什么？', additional_kwargs={}, response_metadata={}),
#     AIMessage(content='刚才我们讨论了今天西安的天气情况，包括气温和天气状况。我提供了一个链接，供你查看更详细的天气信息。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 34, 'prompt_tokens': 4611, 'total_tokens': 4645, 'completion_tokens_details': {'accepted_prediction_tokens': None, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': None}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_29330a9688', 'id': 'chatcmpl-D0iSH3kGO9BkRLSBv525UW9K1Fl86', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--18297182-b024-4717-a6b5-ea420a4e6b82-0', usage_metadata={'input_tokens': 4611, 'output_tokens': 34, 'total_tokens': 4645, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}})], 'llm_calls': 3}

