from xml-rpc.xmlrpcserver import *
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

params = (5,6)

s.register_function(add)

