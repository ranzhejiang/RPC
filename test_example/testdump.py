from xml-rpc.xmlrpcclient import *
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

print(result)



