# 本实验在python3的环境下运行
- client.py是客户端的直接调用代码
- rpclient.py是client.py文件需要调用,查找函数所需的平台化封装方法
- server.py是服务器端直接调用代码
- rpcserver.py是为server.py文件的业务封装,其中有多进程,注册代理等服务
- func_server.py是远端服务器的实现代码
- func_remote.py是func_server.py的函数封装
- func_local.py是rpcserver.py的处理远端服务器的注册请求代码封装
### 运行方法
- 1.首先python server.py,需要保证6226与7042端口没有其他进程占用
- 2.其次运行 python func_server.py,需要保证3111端口没有其他进程占用,这里是远端服务器
- 3.打开几个新的窗口,最好同时运行python client.py,这里是模拟多个客户端进行访问