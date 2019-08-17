#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv
from logging import getLogger

class DataManager:
    def __init__(self, buff_size, output=['csv']):
        self.buff_size = buff_size
        self.output = output
        self.counter = 0
        self.buffer = []

        if 'csv' in self.output:
            self.logger_csv = getLogger('data_manager_csv')
        
        if 'json' in self.output:
            self.logger_json = getLogger('data_manager_json')

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
