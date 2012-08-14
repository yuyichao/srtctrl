# coding=utf-8

#   Copyright (C) 2012~2012 by Yichao Yu
#   yyc1992@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function, division
import time as _time
import re as _re
from .util import *
import datetime

def _try_formats(tstr, formats):
    for f in formats:
        try:
            return _time.strptime(tstr, f)
        except:
            pass
    return

_interval_guesser = [
    [_re.compile("^(?P<sec>[-.0-9]+)s?$"), lambda grp: float(grp("sec"))],
    [_re.compile("^(?P<min>[-.0-9]+)m$"), lambda grp: float(grp("min")) * 60],
    [_re.compile("^(?P<hour>[-.0-9]+)h$"),
     lambda grp: float(grp("hour")) * 3600],
    [_re.compile("^(?P<min>[-.0-9]+)m(?P<sec>[-.0-9]+)s?$"),
     lambda grp: float(grp("sec")) + float(grp("min")) * 60],
    [_re.compile("^(?P<hour>[-.0-9]+)h(?P<min>[-.0-9]+)m$"),
     lambda grp: float(grp("min")) * 60 + float(grp("hour")) * 3600],
    [_re.compile("^(?P<hour>[-.0-9]+)h(?P<min>[-.0-9]+)m(?P<sec>[-.0-9]+)s?$"),
     lambda grp: (float(grp("sec")) + float(grp("min")) * 60
                  + float(grp("hour")) * 3600)],
    [_re.compile("^(?P<hour>[-.0-9]+)h?:(?P<min>[-.0-9]+)m?"
                 ":(?P<sec>[-.0-9]+)s?$"),
     lambda grp: (float(grp("sec")) + float(grp("min")) * 60
                  + float(grp("hour")) * 3600)],
    [_re.compile("^(?P<min>[-.0-9]+)m?:(?P<sec>[-.0-9]+)s?$"),
     lambda grp: float(grp("sec")) + float(grp("min")) * 60],
    ]

def guess_interval(tstr):
    try:
        return float(tstr)
    except:
        pass
    if not isstr(tstr):
        raise ValueError
    tstr = tstr.strip(' \n\r\t\b:').lower()
    try:
        return float(tstr)
    except:
        pass
    for guesser in _interval_guesser:
        try:
            m = guesser[0].search(tstr)
            return float(guesser[1](m.group))
        except:
            pass
    raise ValueError

def guess_time(tstr):
    try:
        return float(tstr)
    except:
        pass
    if not isstr(tstr):
        raise ValueError
    tstr = tstr.strip(' \n\r\t\b:').lower()
    try:
        return float(tstr)
    except:
        pass
    t = _try_formats(tstr, ["%Y:%j:%H:%M:%S", "%Y:%m:%d:%H:%M:%S"])
    if not t is None:
        return _time.mktime(t) - time.timezone
    t = _try_formats(tstr, ["l%Y:%j:%H:%M:%S", "l%Y:%m:%d:%H:%M:%S",
                            "%Y:%j:%H:%M:%Sl", "%Y:%m:%d:%H:%M:%Sl"])
    if not t is None:
        return _time.mktime(t)
    regex = _re.compile("^(ls?t?)?:*(?P<tstr>.*)$")
    res = regex.search(tstr)
    if not res is None:
        try:
            t = guess_interval(res.group("tstr"))
            day = datetime.date.today()
            begin_of_day = _time.mktime(day.timetuple())
            now = _time.mktime()
            t += begin_of_day
            if t < now - 3600:
                t += 86400
            return t
        except:
            pass
    raise ValueError

def try_get_interval(tstr):
    try:
        t = guess_interval(tstr)
        return t
    except:
        pass
    try:
        t = guess_time(tstr) - _time.time()
        return t
    except:
        pass
    return None
