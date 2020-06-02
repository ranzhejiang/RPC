# rpclient.py

import socket as socket
import json
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

    def __getattr__(self, function):

        dict_method = {"sayHello":"test.IHello","add":"add"}
        dict_type = {"<class 'str'>":"string","<class 'int'>":"int"}

        def _func(*args, **kwargs):

            example = {"a_type":["java.lang.String"],"args":["It is Client"],"m_name":"sayHello","s_name":"test.IHello"}
            s_name = dict_method[function]
            a_type = []
            arguments = []
            for term in args:
                pytype = str(type(term))
                standardtype = dict_type[pytype]
                a_type.append(standardtype)
                arguments.append(term)

            d = {'a_type': a_type, 'args': arguments, "m_name": function,"s_name":s_name}
          
            string = json.dumps(d) + "\n"
            self.send(string.encode('utf-8'))
            #self.send(json.dumps(d).encode('utf-8')) # 发送数据
            data = self.recv(1024) # 接收方法执行后返回的结果
            #data = str(data,encoding = "utf-8")
            return data

        setattr(self, function, _func)
        return _func
class RPCClient(TCPClient, RPCStub):
    pass
