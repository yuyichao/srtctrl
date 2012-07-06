# coding=utf-8

def _j_to_str_end(jstr, start):
    l = len(jstr)
    _pass = False
    for i in range(start, l):
        if _pass:
            _pass = False
            continue
        c = jstr[i]
        if c == '"':
            return i + 1
        elif c == '\\':
            _pass = True
    return 0

def _j_find_start(jstr, start):
    l = len(jstr)
    i = start
    while i < l:
        c = jstr[i]
        if c == '"':
            i = _j_to_str_end(jstr, i + 1)
            if i == 0:
                return l
            continue
        elif c in '{}[]':
            return i
        i += 1
    return l

def _j_find_pair(jstr, start=0):
    l = len(jstr)
    start = _j_find_start(jstr, start)
    i = start
    count = {'{}': 0,
             '[]': 0}
    found = False
    while i < l:
        c = jstr[i]
        if c == '"':
            i = _j_to_str_end(jstr, i + 1)
            if i == 0:
                return (start, start)
            continue
        elif c == '{':
            count['{}'] += 1
        elif c == '}':
            count['{}'] -= 1
        elif c == '[':
            count['[]'] += 1
        elif c == ']':
            count['[]'] -= 1
        i += 1
        if count['{}'] or count['[]']:
            found = True
            if count['{}'] < 0 or count['[]'] < 0:
                return start, i
        else:
            if found:
                return start, i
    return start, start

def get_json(jstr, start=0):
    start = start % len(jstr)
    (start1, i) = _j_find_pair(jstr, start=start)
    return (jstr[start:start1], jstr[start1:i], jstr[i:])
