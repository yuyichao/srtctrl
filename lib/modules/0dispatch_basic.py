# coding=utf-8

from srt_comm import *

def dispatch_line(buff):
    (extra, pkg, left) = get_line(buff)
    return (pkg, left)

iface.dispatch.line = dispatch_line

def dispatch_json(buff):
    (extra, pkg, left) = get_json(buff)
    return (pkg, left)

iface.dispatch.json = dispatch_json
