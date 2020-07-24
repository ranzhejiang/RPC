# func_server.py

import func_remote

def rzj(a, b, c=10):
    
    return max(a,b,c)

s = func_remote.Func_server()
s.register_function(rzj) # 注册方法
s.loop(3111) # 传入要监听的端口