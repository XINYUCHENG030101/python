from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from typing_extensions import Annotated

@tool
def add(
        a : Annotated[int, ..., "第一个整数"],
        b : Annotated[int, ..., "第二个整数"],
) -> int:
    """两数相加"""
    return a + b

@tool
def multiply(
        a : Annotated[int, ..., "第一个整数"],
        b : Annotated[int, ..., "第二个整数"],
) -> int:
    """两数相乘"""
    return a * b

model = ChatOpenAI(model="gpt-4o-mini")

# 绑定工具
tools = [add, multiply]
# model_with_tools = model.bind_tools(tools=tools)
# 强制选择工具
model_with_tools = model.bind_tools(tools=tools)

# 调用工具
# print(model_with_tools.invoke("2乘3等于多少？"))
# print(model_with_tools.invoke("你是谁？"))

# 定义消息列表，添加要传递给聊天模型的消息
message = [
    HumanMessage("2乘3等于多少？6加6等于多少？")
]
ai_msg = model_with_tools.invoke(message)
# print(ai_msg)
# tool_calls=[
# {'name': 'multiply', 'args': {'a': 2, 'b': 3}, 'id': 'call_gU6tb6IZ6wkr53RVxTjjK9lH', 'type': 'tool_call'},
# {'name': 'add', 'args': {'a': 6, 'b': 6}, 'id': 'call_j9Dt8oumOcFNDiCnPFw0C4UF', 'type': 'tool_call'}
# ]
message.append(ai_msg)

# 构造ToolMessage, 并添加到消息列表中去
for tool_call in ai_msg.tool_calls:
    selected_tool = {"add": add, "multiply": multiply}[tool_call["name"].lower()]
    tool_msg = selected_tool.invoke(tool_call)
    message.append(tool_msg)

# [
#   HumanMessage(content='2乘3等于多少？6加6等于多少？', additional_kwargs={}, response_metadata={}),
#   AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_DGOoFuAVem6kgZta9KOmoStw', 'function': {'arguments': '{"a": 2, "b": 3}', 'name': 'multiply'}, 'type': 'function'}, {'id': 'call_L4cwhPV7T0fsqF4tJGpCLvMU', 'function': {'arguments': '{"a": 6, "b": 6}', 'name': 'add'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 50, 'prompt_tokens': 99, 'total_tokens': 149, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 0, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_560af6e559', 'id': 'chatcmpl-CQpi4kKZ1uAvsMYsxTB6YU7qjkLvB', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run--4061a22c-0f23-4840-a300-e9e57357214a-0', tool_calls=[{'name': 'multiply', 'args': {'a': 2, 'b': 3}, 'id': 'call_DGOoFuAVem6kgZta9KOmoStw', 'type': 'tool_call'}, {'name': 'add', 'args': {'a': 6, 'b': 6}, 'id': 'call_L4cwhPV7T0fsqF4tJGpCLvMU', 'type': 'tool_call'}], usage_metadata={'input_tokens': 99, 'output_tokens': 50, 'total_tokens': 149, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 0}}),
#   ToolMessage(content='6', name='multiply', tool_call_id='call_DGOoFuAVem6kgZta9KOmoStw'),
#   ToolMessage(content='12', name='add', tool_call_id='call_L4cwhPV7T0fsqF4tJGpCLvMU')
# ]
print(message)
print(model_with_tools.invoke(message).content)


# tool_result = multiply.invoke(ai_msg.tool_calls[0])
# print(tool_result)