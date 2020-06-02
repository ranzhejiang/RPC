# server.py

import rpcserver

def sayHello(str):
   
    return  "server:" + str

def add(a,b):
    return a + b

s = rpcserver.RPCServer()
s.register_function(sayHello) # 注册方法
s.loop(6000) # 传入要监听的端口
