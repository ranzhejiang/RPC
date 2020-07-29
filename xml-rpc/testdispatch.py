from xmlrpcclient import *
import sys
import socket
import urllib
from xml.parsers import expat
from decimal import Decimal
import io
import time

s = ClientStub()

params = (5,6)

result = s.dump(params, "add")

c = ClientRPC()

c.init("192.74.80", 8080)

c.find(6,7)

re = s.dispatch(result)

print(re)