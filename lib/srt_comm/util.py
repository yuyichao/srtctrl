# coding=utf-8

def call_cb(cb, *args):
    if hasattr(cb, '__call__'):
        cb(*args)
