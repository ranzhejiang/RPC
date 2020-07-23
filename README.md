# **A Universal Message - tiny RPC framework -- UM-tRPC**

这是我们的DCE（Distributed Computing Environment)课程的大作业。  
我们小组的成员分别为冉浙江、 郑宇真 和杨立明。

## | **前言**

RPC（Remote Procedure Call）是一种典型的分布计算模型，是面向过程的分布式计算环境的核心架构。远程过程调用是一种像调用本地过程一样调用远程机器上的过程，而不需要了解网络细节的远程过程访问机制。

若对远程过程调用背后的原理和更多的实例感到好奇，可以参考 https://my.oschina.net/hosee/blog/711632

## | **作业要求**

### **设计实现一个简单的RPC框架**

- 不能使用现有的RPC框架，必须基于操作系统Socket接口编程
- 具有一定“平台化”特定：不能只能调用一个特定方法，比如至少能只需要改动一点点就用于另一个方法

### **拓展要求**

- 跨语言调用能力
- IDL和IDL编译器
- 并发模型

## | **分析**

### **架构分析**

软件架构上，实际上我们是通过使用已经在网络环境里普及开的json和xml作为我们的数据包格式，这使得我们的架构天然上存在着跨语言和跨平台调用
- Q
- Qu
- 

### **软件实现分析**

To Be Added (TBA).

### **实验结果分析**

To Be Added (TBA).

## | **总结和思考**




  1. 
  2. 



<img src="docs/figs/framework.png?raw=true" width="600">



``` python
import sys
import socket
import urllib
from xml.parsers import expat
from decimal import Decimal
import io
import time

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
    
    dispatch = {}      # 不同类型的参数使用不同的封装，故按照类型进行分配方法
    dispatch[bool] = dump_bool
    dispatch[int] = dump_int
    dispatch[float] = dump_float
    dispatch[str] = dump_string

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
```



## | **备注**

To Be Added (TBA).