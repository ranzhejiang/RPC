# server.py
# -*- coding: utf-8 -*-
import rpcserver
import asyncore
import os
import time
import numpy as np
from multiprocessing import Process,Queue,Manager,Array

def add(a, b, c=12):
    sum = a + b + c
    return sum
# def close():
#     pass
def func1(q):
    t = rpcserver.func_proxy()
    t.loop_pro(6226,q)

def func2(q):
    s = rpcserver.RPCServer("localhost", 7042, q)
    print("开始完毕")
    s.register_function(add) # 注册方法
# s.register_function(close)
# s.loop(5010) # 传入要监听的端口
m = Manager()
q = m.dict()
print(type(q))
a = Array('u',100)
print("a is first",a)
# p1 = Process(target=func1,args=(q,))
# p2 = Process(target=func2,args=(q,))
# p1.start()
# p2.start()
t = rpcserver.func_proxy()
t.loop_pro(6226,q,a)
print("接下来执行的进程是%d"%(os.getpid()))
print("q is:",q)
s = rpcserver.RPCServer("localhost", 7042,q,a)
s.register_function(add) # 注册方法
# p2.join()
asyncore.loop()
# s = rpcserver.RPCServer("localhost", 7042,q)
# s.register_function(add) # 注册方法
# # s.register_function(close)
# # s.loop(5010) # 传入要监听的端口
# asyncore.loop()