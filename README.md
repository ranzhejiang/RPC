# **A Universal Message - tiny RPC framework -- UM-tRPC**

这是我们的DCE（Distributed Computing Environment)课程的大作业。 

本次大作业的主要工作将分为设计和实现两个部分。我们小组通过多次研讨和分析，最终提出了一个名为 “统一信息格微型RPC架构”的RPC架构，英文全称为 Universed Message tiny RPC（UM-tRPC），下文中都以UM-tRPC代指。设计原则采用了简单化设计。相比于CORBA等以IDL为核心的RPC架构，UM-tRPC避免了复杂的接口描述语言的维护和开发，从而降低了开发者的实现难度与使用者的学习难度。UM-tRPC的核心概念为统一信息格式，即通过统一服务端和客户端两端传送的信息的格式，实现远程过程的调用和跨语言调用能力。即使服务端和客户端使用不同硬件系统和语言进行实现，但由于网络上的数据包格式相同，只要两端都实现了相同的数据包格式的解析就能实现跨语言的调用。

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

UM-tRPC的设计中，我们参考了现在已经存在的json-rpc架构，随着RPC架构的发展，简洁灵活逐渐是各项RPC架构的关键。由于json已经是互联网中大家统一好和达成协议的数据包格式，所以与CORBA不同，即使没有IDL也可以进行跨语言调用。这就大大减少了架构实现和维护的难度和时间。从中，我们抽象出了一个具有泛式意义的RPC架构，即统一信息格式RPC架构。

与之前以IDL为核心，从而实现跨语言跨平台调用的RPC架构不同。UM-tRPC由于统一了在网络中传输的数据包的格式，所以只需要在实际中的客户端和服务端定制好协议，按照约定好的样式设计出对应的解包模块和封装模块就能完成任意语言和平台之间的调用。即此项RPC架构可以理解为应用层上的应用，不受平台的限制。图2-1为UM-tRPC的简单架构图，较为直观的显示了整个架构的组成。
除了设计了统一信息格的RPC架构之外，我们还根据客户端和服务端数量的不同，提出了不同的分布式硬件架构，更加贴切于我们的课程。最初的设想，我们将分布式硬件架构按照实现难度制定了不同的阶段目标，如下所示：
1.	客户端与服务端的单对单架构：只能客户端向服务端发送RPC请求
2.	客户端与服务端的单对多架构：一个客户端对应多个服务端。这意味着提供RPC服务的服务端有多台。这就引入了一个问题，多台服务端提供了不同的远程调用函数，这意味着已经注册的函数能够被客户端所发现。我们是通过提出一个服务节点作为我们的函数表管理节点。加入RPC架构服务的服务端需要首先向服务节点进行函数的注册，而客户端实际上是向固定的服务节点发送RPC请求。
3.	客户端和服务端的多对多架构：实际上，与第二种没有本质上的区别。但在这一阶段我们引入了并发模型，从而缓解大规模请求导致的系统瓶颈。当然，此阶段也将在服务节点引入负载均衡。


### **软件实现分析**

<img src="docs/figs/framework.png?raw=true" width="600">

client端的软件架构：

<img src="docs/figs/client.png?raw=true" width="600">

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

### **实验结果分析**

基于xml格式的message的最终结果实例：

client：
<img src="docs/figs/clientrpc.png?raw=true" width="600">
<img src="docs/figs/clientexamp.png?raw=true" width="600">




server:

<img src="docs/figs/serverrpc.png?raw=true" width="600">
<img src="docs/figs/serverexamp.png?raw=true" width="600">




最终单client对多服务器的架构：


<img src="docs/figs/mult.png?raw=true" width="600">

## | **总结和思考**

  1. 虽然由于是多人合作，中间出现了些许耽搁和开发上的阻力，但是在处理多人协同开发的过程中，锻炼了使用git的能力甚至最后提出了一个git的项目规范。
  2. 此外，还遇到了软件工程方面的问题。正如我们上课时所讲，在一个软件项目的开发中，往往初期的设计会显得非常高大上，但是随着开发的推进，最后的结果往往很不如意。最终，我们还有一些隐藏的bug没能修改，且实现的成果只是个能被称作为玩具的demo。还有，在项目初期制订项目进度时，学生还规划每到一个阶段的节点，就去向老师汇报，并收集老师的意见以改进下一阶段的开发和设计，但最终因为实验室项目和课程等原因，也没能实现。
  3. 但在实际的设计和开发中，学到了很多，也领悟了很多。比如，使用xml作为统一信息格式时，由于其格式处理的复杂性，开发周期相对于json要长很多，而最终的效率却相差无几。这是只有经历一次开发才能明白的事情。此外，在书本中本来显得非常抽象的服务等概念，在我们的实际的开发和讨论中，如硬件架构的分层推进，对这一概念有了更深的领悟。





## | **备注**

本次作业的贡献情况：
<img src="docs/figs/contribute.png?raw=true" width="600">



开发过程中，总分支情况图：


<img src="docs/figs/gitgraph.png?raw=true" width="600">

具体工作：
- xml-rpc: 实现了以xml为基础的RPC与跨语言调用，且在我们的架构上，无需实现IDL。故，可以算是实现了IDL。
- concurrent: 以json为基础，实现了并发模型和单对多架构。