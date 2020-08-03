from xml-rpc.xmlrpcserver import *
from xml-rpc.xmlrpcclient import *
import sys
import socket
import urllib
from xml.parsers import expat
from decimal import Decimal
import io
import time

s = ServerStub()

def add(x, y):
    t = x + y
    return t

s.register_function(add)

c = ClientStub()

params = (6,6)

result = c.dump(params, "add")

re = s.dispatch(result)

print(re)

