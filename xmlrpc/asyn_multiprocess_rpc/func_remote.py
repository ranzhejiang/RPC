import socket as socket
import json
class TCPServer(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind_listen(self, port):
        print("来一次")
        self.sock.bind(('127.0.0.1', port))
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
        print(data)
        print(self.funs)
        method_name = self.data['method_name']
        method_args = self.data['method_args']
        method_kwargs = self.data['method_kwargs']
        res = self.funs[method_name](*method_args, **method_kwargs)
        data = {"res": res}
        return json.dumps(data).encode('utf-8')


class RPCStub(object):
    def __init__(self):
        self.funs = {}

    def register_function(self, function, name=None):
        '''Server端方法注册，Client端只可调用被注册的方法'''
        if name is None:
            name = function.__name__
        self.funs[name] = function
        print("注册完成")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1",6226))
        data = {"func_remote": name,"ip_port":3111}
        data = json.dumps(data).encode('utf-8')
        s.sendall(data)
        s.close()
        print(self.funs)
        
class Func_server(TCPServer, JSONRPC, RPCStub):
    def __init__(self):
        TCPServer.__init__(self)
        JSONRPC.__init__(self)
        RPCStub.__init__(self)

    def loop(self, port):
        # 循环监听 3111 端口
        print("进来一次")
        self.bind_listen(port)
        print("进来一次吗")
        print('Server listen 3111 ...')
        while True:
            self.accept_receive_close()

    def on_msg(self, data):
        return self.call_method(data)