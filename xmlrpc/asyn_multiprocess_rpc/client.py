import rpclient
import time

if __name__ == '__main__':
    print()
    c = rpclient.RPCClient()
    c.connect('127.0.0.1', 7042)
    print("Do you feel well")
    # res2 = c.add(2,100,c=5)
    # print(f'res2: [{res2}]')
    for i in range(10):
        res2 = c.multiply(2,100)
        print(f'res2: [{res2}]')
        res = c.add(1, 3, c=5)
        print(f'res: [{res}]') 
        time.sleep(1)
    # c.close()
