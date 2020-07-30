# server.py
# -*- coding: utf-8 -*-
import rpcserver
import asyncore
import os
import time
import numpy as np
from multiprocessing import Process,Queue,Manager,Array
'''
：初始化中，在服务器端本地注册的函数
'''
def add(a, b, c=12):
    sum = a + b + c
    return sum
'''使用多进程的Manager服务开辟一块固定大小的内存区域，用于多进程通信使用'''
a = Array('u',100)
'''执行远端服务器注册代理服务'''
t = rpcserver.func_proxy()
t.loop_pro(6226,a)
print("当前执行的进程是%d，位置是代理服务进程监听执行退出后"%(os.getpid()))
s = rpcserver.RPCServer("localhost", 7042,a)
s.register_function(add) # 注册方法
asyncore.loop()
# def func1(q):
#     t = rpcserver.func_proxy()
#     t.loop_pro(6226,q)

# def func2(q):
#     s = rpcserver.RPCServer("localhost", 7042, q)
#     print("开始完毕")
#     s.register_function(add) # 注册方法
# s.register_function(close)
# s.loop(5010) # 传入要监听的端口
# p1 = Process(target=func1,args=(q,))
# p2 = Process(target=func2,args=(q,))
# p1.start()
# p2.start()
# s = rpcserver.RPCServer("localhost", 7042,q)
# s.register_function(add) # 注册方法
# # s.register_function(close)
# # s.loop(5010) # 传入要监听的端口
# asyncore.loop()