# rpcserver.py
import socket as socket
import json
class TCPServer(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind_listen(self, port):
        self.sock.bind(('localhost', port))
        self.sock.listen(5)

    def accept_receive_close(self):
        '''获取Client端信息'''
        (client_socket, address) = self.sock.accept()
        msg = client_socket.recv(1024)
        data = self.on_msg(msg)
        client_socket.sendall(data) # 回传
        client_socket.close()


class JSONRPC(object):
    def __init__(self):
        self.data = None

    def from_data(self, data):
        '''解析数据'''
        self.data = json.loads(data.decode('utf-8'))

    def call_method(self, data):
        '''解析数据，调用对应的方法变将该方法执行结果返回'''
        self.from_data(data)
        print("YT")
        print(self.data)
        print()
        method_name = self.data['m_name']
        args = self.data['args']
        #method_kwargs = self.data['method_kwargs']
        res = self.funs[method_name](*args)
        data = {"res": res}
        print(data)
        return json.dumps(data).encode('utf-8')


class RPCStub(object):
    def __init__(self):
        self.funs = {}

    def register_function(self, function, name=None):
        '''Server端方法注册，Client端只可调用被注册的方法'''
        if name is None:
            name = function.__name__
        self.funs[name] = function
        
class RPCServer(TCPServer, JSONRPC, RPCStub):
    def __init__(self):
        TCPServer.__init__(self)
        JSONRPC.__init__(self)
        RPCStub.__init__(self)

    def loop(self, port):
        # 循环监听 6000 端口
        self.bind_listen(port)
        print('Server listen 6000 ...')
        while True:
            self.accept_receive_close()

    def on_msg(self, data):
        return self.call_method(data)
