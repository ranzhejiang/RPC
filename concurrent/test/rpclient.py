# rpclient.py

import socket as socket
import json
class TCPClient(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        
        self.sock.connect((host, port))

    def send(self, data):
        
        self.sock.send(data)

    def recv(self, length):
       
        return self.sock.recv(length)
        

class RPCStub(object):
    def multiply(self,a,b):
        return a*b
    def __getattr__(self, function):
        def _func(*args, **kwargs):
            print(args)
            d = {'method_name': function, 'method_args': args, 'method_kwargs': kwargs}
            print(d)
            #self.send(json.dumps(d).encode('utf-8')) 
            #data = self.recv(1024)
            #return data

        setattr(self, function, _func)
        return _func
class RPCClient(TCPClient, RPCStub):
    pass