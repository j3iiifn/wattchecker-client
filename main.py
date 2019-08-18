#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time
import math

import bluetooth

import wattchecker
from data_manager import DataManager

def configure_logging():
    from logging.config import dictConfig
    import yaml
    with open('logging_config.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        dictConfig(config)

def get_logger():
    from logging import basicConfig, getLogger, DEBUG
    return getLogger(__name__)

configure_logging()
logger = get_logger()

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

    raise Exception('Error: Cannot find MAC address of WATT CHECKER')

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

    raise Exception('Error: Cannot find RFCOMM protocol.')

def search_wattchecker():
    macaddr = _get_macaddr()
    port = _get_port(macaddr)
    return macaddr, port

def main():
    data_manager = DataManager(buff_size=180, output=['csv'])

    mac_address, port = search_wattchecker()
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((mac_address, port))

    try:
        logger.info('Initializing...')
        wattchecker.initialize(s)
        
        logger.info('Starting measurement...')
        wattchecker.start_measure(s)
        
        while True:
            data = wattchecker.get_data(s)
            if data:
                data_manager.store(data)
            now = time.time()
            time.sleep(math.ceil(now) - now)

    finally:
        logger.info('Stopping measurement...')
        wattchecker.stop_measure(s)

        logger.info('Closing socket...')
        s.close()

        logger.info('Saving buffered data...')
        data_manager.dump()


if __name__ == "__main__":
    main()
