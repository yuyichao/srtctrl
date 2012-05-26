#!/usr/bin/env python
# coding=utf-8

_J_RES_OPEN = -1
_J_RES_BLK = -2

def _j_none_blk(jstr, start=0, char=None):
    i = start
    l = len(jstr)
    while i < l:
        if not jstr[i] in _j_blk_chars:
            if not char is None and not jstr[i] in char:
                return
            return i
        i += 1
    return _J_RES_BLK

def _j_to_str_end(jstr, start=0):
    l = len(jstr)
    i = _j_none_blk(jstr, start=start, char='"')
    if i is None:
        return
    if i == _J_RES_BLK:
        return _J_RES_BLK
    while i < l - 1:
        i += 1
        if jstr[i] == '"':
            return i
        elif jstr[i] == '\\':
            i += 1
            if i >= l:
                break
            if jstr[i] == 'u':
                i += 4
            continue
        else:
            pass
    return _J_RES_OPEN

def _j_to_obj_end(jstr, start=0):
    l = len(jstr)
    i = _j_none_blk(jstr, start=start, char='{')
    if i is None:
        return
    if i == _J_RES_BLK:
        return _J_RES_BLK
    while True:
        i += 1
        ni = _j_none_blk(jstr, start=i, char=':,}')
        if ni is None:
            pass
        elif ni == _J_RES_BLK:
            return _J_RES_OPEN
        else:
            if jstr[ni] == '}':
                return ni
            i = ni
            continue
        i = _j_to_all_end(jstr, start=i)
        if i is None:
            return
        if i in (_J_RES_BLK, _J_RES_OPEN):
            return _J_RES_OPEN

def _j_to_arr_end(jstr, start=0):
    l = len(jstr)
    i = _j_none_blk(jstr, start=start, char='[')
    if i is None:
        return
    if i == _J_RES_BLK:
        return _J_RES_BLK
    while True:
        i += 1
        ni = _j_none_blk(jstr, start=i, char=',]')
        if ni is None:
            pass
        elif ni == _J_RES_BLK:
            return _J_RES_OPEN
        else:
            if jstr[ni] == ']':
                return ni
            i = ni
            continue
        i = _j_to_all_end(jstr, start=i)
        if i is None:
            return
        if i in (_J_RES_BLK, _J_RES_OPEN):
            return _J_RES_OPEN

_j_num_possible = '-0123456789.eE+'

# it is hard to tell if a number is finished
def _j_to_num_end(jstr, start=0):
    l = len(jstr)
    i = _j_none_blk(jstr, start=start, char=_j_num_possible)
    if i is None:
        return
    if i == _J_RES_BLK:
        return _J_RES_BLK
    while i < l - 1:
        i += 1
        if not jstr[i] in _j_num_possible:
            return i - 1
    return i

_j_specials = ['true',
               'false',
               'null']
def _j_to_spe_end(jstr, start=0):
    l = len(jstr)
    i = _j_none_blk(jstr, start=start)
    if i == _J_RES_BLK:
        return _J_RES_BLK
    for spe in _j_specials:
        if jstr[i:].lower().startswith(spe):
            i += len(spe)
            if i >= l or jstr[i] in _j_blk_chars:
                return i - 1
            return
    return

_j_to_ends = [_j_to_str_end,
              _j_to_obj_end,
              _j_to_arr_end,
              _j_to_num_end,
              _j_to_spe_end]

_j_blk_chars = ' \t\n\r'

def _j_to_all_end(jstr, start=0):
    i = _j_none_blk(jstr, start=start)
    if i == _J_RES_BLK:
        return _J_RES_BLK
    for _j_to_end in _j_to_ends:
        res = _j_to_end(jstr, start=i)
        # illegal
        if res is None:
            continue
        return res
    return

def __test_str():
    jstrs = ['"',
             '""',
             '"abcd\\a\\u"',
             '"asdf"',
             'asdf']
    for jstr in jstrs:
        print(_j_to_str_end(jstr, start=0))

def __test_all():
    jstrs = ['     []',
             '     {}',
             '  {1:2}',
             '[1, 2,]',
             '1.34.4e',
             '   true',
             '  false',
             '   null']
    print('should be the same')
    for jstr in jstrs:
        print(jstr)
        print(_j_to_all_end(jstr, start=0))

def __test_blk():
    print('\nblk')
    jstrs = ['',
             ' ',
             '  ',
             '0',
             ' 0',
             '  0',
             '   0',
             '    0']
    for jstr in jstrs:
        res = _j_none_blk(jstr)
        print("'%s'" % jstr, res, "'%s'" % jstr[res:] if res >= 0 else 'BLK')
    print('bbbb')
    for jstr in jstrs:
        res = _j_none_blk(jstr, char='0')
        print("'%s'" % jstr, res, ("'%s'" % jstr[res:] if res >= 0 else 'BLK')
              if not res is None else 'Not Match')
    print('bbbb')
    for jstr in jstrs:
        res = _j_none_blk(jstr, char='1')
        print("'%s'" % jstr, res, ("'%s'" % jstr[res:] if res >= 0 else 'BLK')
              if not res is None else 'Not Match')

def __test():
    __test_str()
    __test_blk()
    __test_all()

if __name__ == '__main__':
    __test()
