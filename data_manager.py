#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv

import logging_util
import data_handler

class DataManager:
    def __init__(self, config):
        self.buff_size = config['general']['data_buffer_size']
        self.output = config['general']['data_format']
        self.counter = 0
        self.buffer = []

        if 'csv' in self.output:
            logging_util.configure_logging('logging_config_csv.yaml')
            self.logger_csv = logging_util.get_logger('data_manager_csv')
            self.logger_csv.handlers[0].rotator = data_handler.data_logger_rotator
            self.logger_csv.handlers[0].namer = data_handler.data_logger_namer
        
        if 'json' in self.output:
            logging_util.configure_logging('logging_config_json.yaml')
            self.logger_json = logging_util.get_logger('data_manager_json')
            self.logger_json.handlers[0].rotator = data_handler.data_logger_rotator
            self.logger_json.handlers[0].namer = data_handler.data_logger_namer

    def store(self, data):
        """Store data to buffer.

        Args:
            data (dict): For example: {"datetime": "2019-08-16 15:35:19", "V": 104.819, "mA": 217.9609375, "W": 0.76}
        """
        self.buffer.append(data)
        self.counter += 1

        if self.counter >= self.buff_size:
            self.dump()

    def dump(self):
        if 'csv' in self.output:
            self.write_csv()

        if 'json' in self.output:
            self.write_json()
        
        self.counter = 0
        self.buffer = []
    
    def write_csv(self):
        for d in self.buffer:
            self.logger_csv.info('{},{:.2f},{:.2f},{:.2f}'.format(d['datetime'], d['V'], d['mA'], d['W']))
    
    def write_json(self):
        for d in self.buffer:
            self.logger_json.info(json.dumps(d))
