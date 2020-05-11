# rpcserver.py
# -*- coding: utf-8 -*-
import socket as socket
import json
import asyncore
import os
from io import BytesIO as StringIO
import time
import struct

class RPCStub(object):
    def __init__(self):
        self.funs = {}

    def register_function(self, function, name=None):
        '''Server端方法注册，Client端只可调用被注册的方法'''
        if name is None:
            name = function.__name__
        self.funs[name] = function
        
class RPCServer(RPCStub,asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        RPCStub.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr() # 让侦听同一个服务器端口的多个客户端可以公用这个端口，以便多进程并发竞争
        self.bind((host, port))
        self.listen(1)
        self.prefork(10)  # 开辟10个子进程

    def prefork(self, n):
        '''参照tornado的高并发模式进行prefork操作'''
        for i in range(n):
            pid = os.fork()
            if pid < 0:  # fork error
                return
            if pid > 0:  # parent process
                continue
            if pid == 0:
                break  # child process

    def handle_accept(self):
        '''处理任意客户端的连接请求'''
        pair = self.accept()  # 获取一个连接
        if pair is not None:
            sock, addr = pair
            RPCHandler(sock, addr, self.funs)  # 处理连接，需要传入注册的函数


class JSONRPC(object):
    '''json数据的处理'''
    def __init__(self):
        self.data = None

    def from_data(self, data):
        '''解析数据'''
        self.data = json.loads(data)

    def call_method(self, data):
        '''解析数据，调用对应的方法变将该方法执行结果返回'''
        self.from_data(data)
        method_name = self.data['method_name'] 
        method_args = self.data['method_args']
        method_kwargs = self.data['method_kwargs']
        res = self.funs[method_name](*method_args, **method_kwargs)
        data = {"res": res}
        return json.dumps(data).encode()

class RPCHandler(asyncore.dispatcher_with_send,JSONRPC):
    def __init__(self,sock,addr,funs):
        asyncore.dispatcher_with_send.__init__(self, sock=sock)
        JSONRPC.__init__(self)
        self.addr = addr
        self.rbuf = StringIO() #这是服务器用来接收客户端消息的用户定义缓冲，注意这里不同于socket的套接字缓冲
        self.funs = {}  # 用来重定向注册时的远程函数指向，使得可以跨类调用
        self.funs = funs

    def handle_close(self):
        '''客户端退出执行的操作，ctrl+c or 正常结束客户端'''
        print (self.addr, 'bye')
        self.close()
    
    def on_msg(self, data):
        '''处理消息的函数'''
        return self.call_method(data)

    def handle_read(self):
        '''服务器收到客户端请求发生的读消息操作，只要客户端一发就侦测执行'''
        while True: #异步的时候，需要保证消息达到一定数量完整执行，防止消息体过大造成异步处理错误
            msg = self.recv(1024)
            if msg:
                self.rbuf.write(msg)
            if len(msg) < 1024:
                break

        while True:
            self.rbuf.seek(0) #读的时候，先将游标置头
            length_header = self.rbuf.read(4)
            if len(length_header) < 4:  # 半包
                print("打印半包头信息,它的长度为：",len(length_header))
                break
            body_length, = struct.unpack("I", length_header) #读取消息头指定的消息体长度
            msg_body = self.rbuf.read(body_length)
            if len(msg) < body_length:
                print("打印半包体信息,它的长度为：",len(msg_body))
                break               
            data = self.on_msg(msg_body)
            print(os.getpid(),"发送的数据为",data.decode('utf-8'))
            self.send(data)
            left = self.rbuf.getvalue()[body_length + 4:]  # 将读缓冲截取，重新往复写消息
            self.rbuf = StringIO()
            self.rbuf.write(left)
        self.rbuf.seek(0, 2) # 移动游标到缓冲区末尾，便于后续内容直接追加(写是从尾到头写)