# func_server.py

import func_remote

def max_num(a, b, c=10):
    
    return max(a,b,c)

s = func_remote.Func_server()
s.register_function(max_num) # 注册方法
s.loop(2000) # 传入要监听的端口