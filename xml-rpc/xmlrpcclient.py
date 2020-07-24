import sys
import socket
import urllib
from xml.parsers import expat
from decimal import Decimal
import io
import time
import string

__version__ = '%d.%d' % sys.version_info[:2]

def escape(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    return s

class Parser:
    # fast expat parser for Python 2.0 and later.
    def __init__(self, target):
        self._parser = parser = expat.ParserCreate(None, None)
        self._target = target
        parser.StartElementHandler = target.start
        parser.EndElementHandler = target.end
        parser.CharacterDataHandler = target.data

    def feed(self, data):
        self._parser.Parse(data, False)

    def close(self):
        try:
            parser = self._parser
        except AttributeError:
            pass
        else:
            del self._target, self._parser 
            parser.Parse(b"", True) 

class Marshaller:
    # xml文件封包器
    def __init__(self, encoding):
        self.mem = {}
        self.data = None
        self.encoding = encoding

    def dumps(self, values):
        out = []
        write = out.append
        dump = self._dump
        write("<parameter>\n")
        for v in values:
            write("<param>\n")
            dump(v,write)
            write("</param>\n")
        write("</parameter>\n")
        result = "".join(out)
        return result

    def _dump(self, value, write):
        # 判断能否解析目标参数类型, 并使用对应函数
        try:
            d = self.dispatch[type(value)]
        except KeyError:
            if not hasattr(value, '_dict_'):
                raise TypeError("sorry, can't marshall %s objects" % type(value))
        d(self, value, write)

    def dump_bool(self, value, write):
        write("<value><boolean>")
        write(value and "1" or "0")
        write("/<boolean></value>\n")
    

    def dump_int(self, value, write):
        write("<value><int>")
        write(str(int(value)))
        write("</int></value>\n")
    

    def dump_float(self, value, write):
        write("<value><float>")
        write(str(float(value)))
        write("</float></value>\n")
    

    def dump_string(self, value, write, escape):
        write("<value><string>")
        write(escape(value))       # 替换特殊符号
        write("</string></value>\n")
    

    def dump_list(self, value, write): # ?????
        write("<value><list>")

    dispatch = {}      # 不同类型的参数使用不同的封装，故按照类型进行分配方法
    dispatch[bool] = dump_bool
    dispatch[int] = dump_int
    dispatch[float] = dump_float
    dispatch[str] = dump_string

class UnMarshaller:
    def __init__(self):
        self._type = None
        self._stack = []
        self._marks = []  # 用于后续的list等数据格式的解析
        self._data = []
        self._flag = False
        self._methodname = None
        self._encoding = "utf-8"
        self.append = self._stack.append
    
    def getMethodName(self):
        return self._methodname
    
    def start(self, tag, attrs):
        if tag == "RPCCall":
            self._flag = True
        if self._flag:
            self._data = []
        else :
            print("this response is error")
            
    
    def data(self, data):
        if self._flag:
            self._data.append(data)
    
    def end(self, tag):
        if self._flag:
            try:
                function = self.dispatch[tag]
            except KeyError:
                if ':' not in tag:
                    return 
                try:
                    function = self.dispatch[tag.split(':')[-1]]
                except KeyError:
                    return 
            function(self, "".join(self._data))
    
    def finish(self):
        return tuple(self._stack)

    def do_boolean(self, data):
        if data == "0":
            self.append(False)
        elif data == "1":
            self.append(True)
        else:
            raise TypeError("bad boolean value")

    def do_int(self, data):
        self.append(int(data))

    def do_float(self, data):
        self.append(float(data))
    

    def do_string(self, data):
        self.append(data)
    

    def do_list(self, data):    # not complete
        mark = self._marks.pop()
        self._stack[mark:] = [self._stack[mark:]]

    def do_parameter(self, data):
        self._type = "parameter"
 

    def do_methodName(self, data):   #多进程时的可扩展性
        self._methodname = data
        self._type = "methodName"

    def do_value(self, data):
        self._type = "value"
    
    dispatch = {}
    dispatch["boolean"] = do_boolean
    dispatch["int"] = do_int
    dispatch["float"] = do_float
    dispatch["string"] = do_string
    dispatch["methodName"] = do_methodName
    dispatch["parameter"] = do_parameter
    dispatch["value"] = do_value

    

class ClientStub:
    
    def dump(self, params, methodname = None):
        encoding = "utf-8"
        m = Marshaller(encoding)
        data = m.dumps(params)
        xmlheader = "<?xml version='1.0'?>\n"
        if methodname:
            data = (
                xmlheader,
                "<RPCCall>/n"
                "<methodName>", methodname, "</methodName>\n",
                data,
                "</RPCCall>\n"
            )
        return "".join(data)
    
    def dispatch(self, data):
        u = UnMarshaller()
        p = Parser(u)
        p.feed(data)
        p.close()
        return u.finish() #u.getMethodName()

class Transport:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self, host, port):
        self.sock.connect((host, port))
    
    def send(self, data):
        self.sock.send(data)
    
    def recv(self, length):
        return self.sock.recv(length)


class ClientRPC:
    def __init__(self):
        self._transport = None
        self._clientstub = None
        self._request_list = []
    
    def __getattr__(self, function):
        def method(*args):
            self._request_list.append(function)
            print(args)
            print(function)
            return self._clientstub.dump(args, function)
        setattr(self, function, method)
        data = method()
        print(data)
        #self.send(data)
        #response = self.recv()
        #return response

        
    def init(self,host, port):
        t = Transport()
        s = ClientStub()
        self._transport = t
        self._clientstub = s
       # self._transport.connect(host, port)
    
    def send(self, data):
        self._transport.send(data)
    
    def recv(self, length = 1024):
        return self._transport.recv(length)



    
    
    