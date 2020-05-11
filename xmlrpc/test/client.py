import rpclient

c = rpclient.RPCClient()
c.connect('127.0.0.1', 1777)
res2 = c.multiply(2,100)
print(f'res2: [{res2}]')
res = c.add(1, 2, c=5)
print(f'res: [{res}]')
