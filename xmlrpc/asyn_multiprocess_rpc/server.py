# server.py
# -*- coding: utf-8 -*-
import rpcserver
import asyncore

def add(a, b, c=12):
    sum = a + b + c
    return sum
# def close():
#     pass
s = rpcserver.RPCServer("localhost", 7042)
s.register_function(add) # 注册方法
# s.register_function(close)
# s.loop(5010) # 传入要监听的端口
asyncore.loop()
