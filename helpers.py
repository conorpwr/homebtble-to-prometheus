# Modified version of helpers.py for this project
# Orignal code can be found at: https://github.com/custom-components/ble_monitor/tree/master/custom_components/ble_monitor/ble_parser
# Original license applies (MIT) - https://github.com/custom-components/ble_monitor/blob/master/LICENSE

"""Helpers for bleparser"""
from uuid import UUID


def to_uuid(uuid: str) -> str:
    """Return formatted UUID"""
    return str(UUID(''.join(f'{i:02X}' for i in uuid)))


def to_mac(addr: str) -> str:
    """Return formatted MAC address"""
    return ':'.join(f'{i:02X}' for i in addr)


def to_unformatted_mac(addr: str) -> str:
    """Return unformatted MAC address"""
    return ''.join(f'{i:02X}' for i in addr[:])
