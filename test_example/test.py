import sys

class Test:
    def __init__(self):
        self._test = 20
    
    def __getattr__(self, function):
        def func(*args, **kwargs):
            print(function)
            print("hello,world")
        func()

    
    def __call__(self):
        print(self._test)

if __name__ == "__main__":

    t = Test()
    t.test()