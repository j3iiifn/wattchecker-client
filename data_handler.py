#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import shutil
import os

def _gzip_file(source, destination):
    with open(source, 'rb') as f_in:
        with gzip.open(destination, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    os.remove(source)

def data_logger_namer(name):
    return name + ".gz"

def data_logger_rotator(source, destination):
    _gzip_file(source, destination)
