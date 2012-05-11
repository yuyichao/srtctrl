#!/usr/bin/env python

import os, socket, fcntl
from time import sleep

from .srtbase import *
from .srtsock import *
from gi.repository import Gio

class SrtConnBase(SrtBase):
    __gsignals__ = {
    }
    _conf = {'host': 'localhost',
             'port': 1421}
    def __init__(self, conf={}):
        super().__init__(conf=conf)
        self._sock = SrtSock(conf=conf)

    conn_state = GObject.Property(type=int)
