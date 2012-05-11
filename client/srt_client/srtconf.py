#!/usr/bin/env python

from os import path
import inspect

try:
    execfile
except NameError:
    def execfile(file, globals=globals(), locals=locals()):
        with open(file, "r") as fh:
            code = compile(fh.read() + "\n", file, 'exec')
        exec(code, globals, locals)

srt_dir_name = path.dirname(__file__)
if srt_dir_name == '':
    srt_dir_name = '.'
srt_dir_name = path.abspath(srt_dir_name)
__file_name = path.basename(__file__)

def_cfg_f = "%s/srtpara.py" % srt_dir_name
def_cfg = {}
execfile(def_cfg_f, {}, def_cfg)

def updata_kwargs(new_dict, **defaults):
    return update_select(new_dict, defaults)

def update_select_diff(new_dict, defaults):
    res = {}
    diff = False
    for key, value in defaults.items():
        if key in new_dict:
            res[key] = new_dict[key]
            if new_dict[key] != value:
                diff = True
        else:
            res[key] = value
    return diff, res

def update_select(new_dict, defaults):
    diff, res = update_select_diff(new_dict, defaults)
    return res
