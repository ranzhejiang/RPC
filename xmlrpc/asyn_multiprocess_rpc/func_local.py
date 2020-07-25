# func_local.py
# 负责处理本地服务器

import socket as socket
import json
import os
class TCPClient(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        '''链接Server端'''
        self.sock.connect((host, port))

    def send(self, data):
        '''将数据发送到Server端'''
        self.sock.send(data)

    def recv(self, length):
        '''接受Server端回传的数据'''
        return self.sock.recv(length)
        

class RPCStub(object):
    def multiply(self,a,b):
        return a*b
    def __getattr__(self, function):
        def _func(*args, **kwargs):
            # print("function is:",type(function))
            # print("args is:",args[0],type(args[0]))
            d = {'method_name':args[0], 'method_args': args[1:], 'method_kwargs': kwargs}
            self.send(json.dumps(d).encode('utf-8')) # 发送数据
            data = self.recv(1024) # 接收方法执行后返回的结果
            return data
        print("开始发送本地服务器到远端服务器的消息请求，本进程为:",os.getpid())
        setattr(self, function, _func)
        return _func
class Func_local(TCPClient, RPCStub):
    pass