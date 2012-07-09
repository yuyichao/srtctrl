# coding=utf-8

print('module1 loading')
iface.test.func1 = lambda: [1, 2]

def func2(i):
    i = iface.test2.func2(i)
    return i**2

iface.test.func2 = func2
print('module1 loaded')
