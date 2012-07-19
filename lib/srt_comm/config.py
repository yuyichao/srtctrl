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

"""
Handle Default Configuration and Environment Variables
"""

from __future__ import print_function, division
from . import _config
from .util import read_env
from os import path

SRT_MODULES_PATH = read_env('SRT_MODULES_PATH',
                            default=_config.SRT_MODULES_PATH, append=':')
SRT_CONFIG_PATH = read_env('SRT_CONFIG_PATH', default=_config.SRT_CONFIG_PATH,
                            append=':')
SRT_HELPER = read_env('SRT_HELPER_PATH', default=_config.SRT_HELPER_PATH)
SRT_HELPER = path.abspath(SRT_HELPER) + '/srt_helper.py'
SRT_INITIALIZER = read_env('SRT_INITIALIZER', default=_config.SRT_INITIALIZER)
