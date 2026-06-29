
import redis

redis_url = "redis://192.168.100.238:6379"
# 定义Redis客户端
redis_client = redis.from_url(redis_url)
# Ping
print(redis_client.ping())