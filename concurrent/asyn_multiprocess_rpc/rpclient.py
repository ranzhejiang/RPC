# rpclient.py

import socket as socket
import json
import struct

class TCPClient(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        '''链接Server端'''
        self.sock.connect((host, port))

    def send(self, data):
        '''将数据发送到Server端'''
        print()
        print()
        self.sock.sendall(data)

    def recv(self, length):
        '''接受Server端回传的数据'''
        return self.sock.recv(length)
        

class RPCStub(object):
    def multiply(self,a,b):
        return a*b
    def __getattr__(self, function):
        '''所有不在本地的函数都会这里集中rpc发送处理'''
        def _func(*args, **kwargs):
            d = {'method_name': function, 'method_args': args, 'method_kwargs': kwargs}
            request = json.dumps(d).encode()
            length_prefix = struct.pack("I", len(request))
            self.send(length_prefix) #发送数据的长度
            self.send(request) # 发送数据
            print("已经发送")
            data = self.recv(1024) # 接收方法执行后返回的结果
            return data.decode()

        setattr(self, function, _func)
        return _func
class RPCClient(TCPClient, RPCStub):
    pass