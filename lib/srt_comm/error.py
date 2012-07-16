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
from .util import *

def_enum(
    'SRTERR_CONN', # connection lost or other connection errors
    'SRTERR_BUSY', # resources busy
    'SRTERR_PLUGIN', # plugin of required type/name cannot been found
    'SRTERR_HELPER_QUIT', # helper quit
    'SRTERR_UNKNOWN_REPLY', # unkown reply from remote server
    'SRTERR_UNKNOWN_CMD', # unknown command from user
    'SRTERR_GENERIC_REMOTE', # generic remote error
    'SRTERR_GENERIC_LOCAL', # generic local error
    'SRTERR_LAST'
    )
