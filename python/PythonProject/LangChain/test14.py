# 同步IO
# import time
#
#
# def boil_water():
#     print("开始烧水...")
#     time.sleep(5)     # 模拟烧水5s, CPU 完全空闲
#     print("烧水完成...")
#
# def send_message():
#     print("开始发消息...")
#     time.sleep(2)  # 模拟烧水2s
#     print("发消息完成...")
#
# def main():
#     # 1、烧水
#     boil_water()
#     # 2、发消息
#     send_message()
#
# # 共耗时7s
# main()

# 异步 IO
import asyncio

# 协程
async def boil_water_async():
    print("开始烧水...")
    await asyncio.sleep(5)  # 关键！ await表示等待这个操作完成，但期间可以做别的事
    print("烧水完成...")
# 协程
async def send_message_async():
    print("开始发消息...")
    await asyncio.sleep(2)  # 模拟烧水2s
    print("发消息完成...")

# 协程：调度
# 事件循环
async def main():
    # 1、烧水（任务）
    task1 = asyncio.create_task(boil_water_async())
    # 2、发消息（任务）
    task2 = asyncio.create_task(send_message_async())
    await task1
    await task2

# 5s
# run 会创建一个事件循环
asyncio.run(main())
