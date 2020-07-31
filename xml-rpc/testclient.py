from xmlrpcclient import *

client = ClientRPC()

client.init('localhost', 5000)

result = client.add(5,6)

print(result)

re = client.addmulti(10,11)

print(re)