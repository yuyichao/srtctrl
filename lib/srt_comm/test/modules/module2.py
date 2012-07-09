# coding=utf-8

print('module2 loading')
iface.test2.func1 = lambda: [1, 2]

def func2(i):
    return i**3

iface.test2.func2 = func2
iface.test2.func3 = iface.test3.func1
print('module2 loaded')
