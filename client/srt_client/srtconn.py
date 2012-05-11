#!/usr/bin/env python

import os, socket, fcntl
from time import sleep

from .srtbase import *

def SrtConnBase(SrtBase):
    _conf = {'host': 'localhost',
             'port': 1421}
    def __init__(self, conf={}):
        super().__init__(conf=conf)
