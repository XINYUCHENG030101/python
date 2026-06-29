import uuid

from langchain.embeddings import init_embeddings
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import PostgresStore

# 1. 内存级 store
# store = InMemoryStore(
#     index={
#         "embed": init_embeddings("openai:text-embedding-3-small"),  # 嵌入模型
#         "dims": 1536,      # 向量维度
#         "fields": ["$"]    # 对value中的所有字段进行嵌入
#     }
# )
#
# # store 基本使用
#
# # 2. 定义命名空间
# # 用于组织记忆，通常按照业务进行划分，例如：定制化智能助手需要用用户id进行隔离
# user_id = "user_123"
# # user_id2 = "user_456"
# namespace_1 = (user_id, "prefs", "food")
# namespace_2 = (user_id, "prefs", "music")
#
# # 3. 存入的一条记忆
# memory_id_1 = str(uuid.uuid4())
# memory_value_1 = {"xi": "披萨"}
# memory_id_2 = str(uuid.uuid4())
# memory_value_2 = {"china": "夜曲"}
#
# # 4. 记忆存储
# store.put(namespace=namespace_1, key=memory_id_1, value=memory_value_1)
# store.put(namespace=namespace_2, key=memory_id_2, value=memory_value_2)
#
#
# # 5. 记忆读取
# # store.get(namespace_1, memory_id_1)
# # all = store.search((user_id, "prefs", ))
# # for mem in all:
# #     print(mem.dict())   # 将记忆对象转成字典查看
#
# # store 支持语义搜索
# # query 参数可以按照语义进行搜索
# all = store.search((user_id, "prefs", ), query="用户喜欢的中国音乐", limit=1)
# for mem in all:
#     print(mem.dict())   # 将记忆对象转成字典查看

# 2. Postgres store
DB_URI = "postgresql://postgres:bit@192.168.100.233:5432/postgres"
with (
    PostgresSaver.from_conn_string(DB_URI) as checkpointer,
    PostgresStore.from_conn_string(DB_URI) as store,
):
    # 第一次 setup
    # store.setup()
    user_id = "user_123"
    namespace_1 = (user_id, "prefs", "food")
    memory_id_1 = "8ddfea24-ca22-4508-a254-0d156783cde5"
    memory_value_1 = {"xi": "披萨"}
    # store.put(namespace=namespace_1, key=memory_id_1, value=memory_value_1)
    # 记忆读取
    print(store.get(namespace_1, memory_id_1))


