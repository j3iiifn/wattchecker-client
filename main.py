#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import time
import math

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

def main():
    configure_logging()
    logger = get_logger()

    data_manager = DataManager(buff_size=180, output=['csv'])

    serverMACAddress = 'WATTCHECKER_MAC_ADDRESS'
    port = 6
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((serverMACAddress, port))

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
