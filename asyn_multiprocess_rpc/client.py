import rpclient
import time

if __name__ == '__main__':
    c = rpclient.RPCClient()
    c.connect('127.0.0.1', 7042)
    for i in range(10):
        res2 = c.rzj(2,70,180)
        print(f'res2: [{res2}]')
        res = c.add(1,2,3)
        print(f'res: [{res}]') 
        time.sleep(1)
    # c.close()
