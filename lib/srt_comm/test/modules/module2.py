# coding=utf-8

print('module2 loading')
setiface.test2.func1 = lambda: [1, 2]

def func2(i):
    return i**3

setiface.test2.func2 = func2
setiface.test2.func3 = getiface.test3.func1
setiface.test2.fkkkk.llll.i = [1, 2, 3, 4]
print('module2 loaded')
