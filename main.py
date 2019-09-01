#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time
import math

import bluetooth

import wattchecker
from data_manager import DataManager
import logging_util

BUFF_SIZE = 180  # seconds
OUTPUT_FORMAT = ['csv']

logging_util.configure_logging('logging_config_main.yaml')
logger = logging_util.get_logger(__name__)

def _get_macaddr():
    """Discover WATT CHECKER and get MAC address of it

    Return:
        string: a mac address of WATT CHECKER
    """
    logger.info('Discovering WATT CHECKER...')
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    for addr, name in nearby_devices:
        if name == 'WATT CHECKER':
            return addr

    raise Exception('Error: Failed to find MAC address of WATT CHECKER')

def _get_port(mac_address):
    """Get port number of RFCOMM protocol
    * Prerequisites: paired to WATT CHECKER with bluetoothctl command.
    
    Args:
        mac_address (string): a MAC address of WATT CHECKER

    Return:
        int: a port number of RFCOMM protocol
    """
    logger.info('Searching RFCOMM service...')
    services = bluetooth.find_service(address=mac_address)
    for s in services:
        if s['protocol'] == 'RFCOMM':
            return s['port']

    raise Exception('Error: Failed to find RFCOMM protocol.')

def search_wattchecker():
    macaddr = _get_macaddr()
    port = _get_port(macaddr)
    return macaddr, port

def connect_wattchecker(mac_address, port):
    while True:
        try:
            logger.info('Connecting to %s %s ...' % (mac_address, port))
            s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            s.connect((mac_address, port))
        except OSError as e:
            logger.error('Failed to connect to %s %s: %s' % (mac_address, port, e))
            time.sleep(60)
        else:
            return s

def main():
    data_manager = DataManager(buff_size=BUFF_SIZE, OUTPUT_FORMAT)

    mac_address, port = search_wattchecker()
    s = connect_wattchecker(mac_address, port)

    try:
        logger.info('Initializing...')
        wattchecker.initialize(s)
        
        logger.info('Starting measurement...')
        wattchecker.start_measure(s)
        
        while True:
            try:
            data = wattchecker.get_data(s)
            if data:
                data_manager.store(data)
            now = time.time()
            time.sleep(math.ceil(now) - now)
            except OSError as e:
                logger.error('Failed to get data: %s' % e)

                s = connect_wattchecker(mac_address, port)

                logger.info('Initializing...')
                wattchecker.initialize(s)
                
                logger.info('Starting measurement...')
                wattchecker.start_measure(s)

    finally:
        try:
        logger.info('Stopping measurement...')
        wattchecker.stop_measure(s)

        logger.info('Closing socket...')
        s.close()
        except Exception as e:
            logger.error('Failed to close connection: %s' % e)

        logger.info('Saving buffered data...')
        data_manager.dump()


if __name__ == "__main__":
    main()
