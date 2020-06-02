import rpclient

c = rpclient.RPCClient()
c.connect('localhost', 6000)
#res2 = c.add(2,100)
#print(f'res2: [{res2}]')
res = c.sayHello("It is cient")
print(f'res: [{res}]')
