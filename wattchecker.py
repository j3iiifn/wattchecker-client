#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import time

import logging_util
logger = logging_util.get_logger(__name__)

from datetime import datetime, timedelta, timezone

import crcmod
crc8_func = crcmod.mkCrcFun(0x185, initCrc=0, rev=False)

def crc8(data):
    """Calcurate CRC8

    >>> crc8(bytes.fromhex('01 0e 3b 0d 11 08 13 05'))
    b'\xe1'

    >>> crc8(bytes.fromhex('08'))
    b'\xb3'

    >>> crc8(bytes.fromhex('01 00'))
    b'\x97'

    Args:
        data (bytes): 
    
    Return:
        bytes: CRC8 value
    """
    return crc8_func(data).to_bytes(1, 'big')


PACKET_HEADER = 0xAA
COMMAND_RTC_TIMER = 0x01
COMMAND_START_MEASURE = 0x02
COMMAND_STOP_MEASURE = 0x03
COMMAND_GET_DATA = 0x08


def initialize(socket):
    """Request initialization to WATT CHECKER"""
    now = datetime.now(timezone.utc)
    payload = bytes([
        COMMAND_RTC_TIMER, 
        now.second, 
        now.minute, 
        now.hour, 
        now.day, 
        now.month, 
        now.year%100, 
        now.weekday()
        ])
    _request(socket, payload)

def start_measure(socket):
    """Request starting measurement to WATT CHECKER"""
    payload = bytes([
        COMMAND_START_MEASURE,
        0x00
    ])
    _request(socket, payload)

def stop_measure(socket):
    """Request stopping measurement to WATT CHECKER"""
    payload = bytes([
        COMMAND_STOP_MEASURE
    ])
    _request(socket, payload)

def get_data(socket):
    """Get measurement data from WATT CHECKER"""
    payload = bytes([
        COMMAND_GET_DATA
    ])
    try:
        response = _request(socket, payload)
        return _unpack_data(response)
    except Exception as e:
        logger.warning(e)
        return None

def _unpack_data(buffer):
    """Unpack received data

    >>> d = _unpack_data(bytes.fromhex('AA 11 00 08 00 BC 6E 00 3E 9C 01 89 00 00 1E 26 0F 0F 08 13 9E'))
    >>> d == {"datetime": "2019-08-15 15:38:30", "V": 105.534, "mA": 221.46875, "W": 0.685}
    True
    
    Args:
        buffer (bytes): Data received from WATT CHECKER

    Returns:
        dict: A dictinary contains unpacked data. For example:
            {"datetime": "2019-08-16 14:30:27", "V": 103.779, "mA": 220.0859375, "W": 0.63}
            * time zone of datetime is UTC.
    """
    field_lengths = (
        ('header', 1),  # 0
        ('length', 2),  # 1, 2
        ('command', 1),  # 3
        ('error_code', 1),  # 4
        ('current', 3),  # 5, 6, 7
        ('voltage', 3),  # 8, 9, 10
        ('power', 3),  # 11, 12, 13
        ('second', 1),  # 14
        ('minute', 1),  # 15
        ('hour', 1),  # 16
        ('day', 1),  # 17
        ('month', 1),  # 18
        ('year', 1)  # 19
    )
    d = {}
    i = 0
    for k, l in field_lengths:
        v = int.from_bytes(buffer[i:i+l], 'little')
        d[k] = v
        i += l

    ret = {}
    ret['datetime'] = datetime(2000 + d['year'], d['month'], d['day'], d['hour'], d['minute'], d['second']).strftime('%Y-%m-%d %H:%M:%S')
    ret['V'] = d['voltage'] / 1000.0
    ret['mA'] = d['current'] / 128.0
    ret['W'] = d['power'] * 5.0 / 1000.0

    return ret

def _request(socket, payload):
    command = b''.join([
        struct.pack('B', PACKET_HEADER),
        struct.pack('<H', len(payload)),
        payload,
        crc8(payload)
    ])

    logger.debug("Send: %s" % command.hex())
    socket.send(command)

    response = socket.recv(1024)
    logger.debug("Receive: %s" % response.hex())

    header = response[0]
    if header != PACKET_HEADER:
        raise Exception('Error: Received invalid packet header from WATT CHECKER. %s' % response.hex())

    error_code = response[4]
    if error_code != 0x00:
        raise Exception('Error: Received error code from WATT CHECKER. %s' % response.hex())
    
    return response
