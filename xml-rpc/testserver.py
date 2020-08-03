from xmlrpcserver import *

def add(x,y):
    t = x + y
    return t
    
def addmulti(x,y):
    t = x + y
    t = x * y * t
    return t

server = ServerRPC()

server.init('localhost', 5000)

server.add_func(add)
server.add_func(addmulti)

while True:
    data = server.recv(1024)
    send = server.response(data)
    server.send(send)


