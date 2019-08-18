#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def configure_logging(config_file):
    from logging.config import dictConfig
    import yaml
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f.read())
        dictConfig(config)

def get_logger(name):
    from logging import getLogger
    return getLogger(name)
