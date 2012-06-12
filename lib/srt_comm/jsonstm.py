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

def _j_is_common(char):
    char = char[0]
    return ((char in '_-.+') or ('a' <= char <= 'z') or ('A' <= char <= 'Z')
            or ('0' <= char <= '9'))

def _j_to_common_end(jstr, start=0):
    l = len(jstr)
    i = _j_none_blk(jstr, start=start)
    if not _j_is_common(jstr[i]):
        return
    if i == _J_RES_BLK:
        return _J_RES_BLK
    while i < l - 1:
        i += 1
        if not _j_is_common(jstr[i]):
            return i - 1
    return i

_j_to_ends = [_j_to_str_end,
              _j_to_obj_end,
              _j_to_arr_end,
              _j_to_common_end]

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

def get_json(jstr, start=0):
    res = _j_to_all_end(jstr, start=start)
    if res is None:
        return (None, jstr)
    if res == _J_RES_BLK:
        return ('', '')
    i = res + 1
    return (jstr[:i], jstr[i:])
