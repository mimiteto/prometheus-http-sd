#! /usr/bin/env python3

""" Module provides utils to generate targets based on ip adddresses """

import socket
from ipaddress import (
    IPv4Address, IPv4Network, AddressValueError, NetmaskValueError
)
from contextlib import closing

from prom_http_sd.models.targets import Target, PortNumber
from prom_http_sd.models.util_types import (
    IPv4NetworkStr,
    UTIL_REGISTRY,
)


def get_hosts_for_network(network: IPv4NetworkStr) -> list[IPv4Address]:
    """
    Function returns a list of ipv4 addresses that are contained within provided network.
    Raises NotImplementedError if the network is not IPv4 network.
    """
    try:
        return list(IPv4Network(network, strict=False).hosts())
    except (AddressValueError, NetmaskValueError) as exc:
        raise NotImplementedError(
            f"{network} is not a valid IPv4 network. IPv6 networks are not supported."
        ) from exc


def check_host(host: IPv4Address) -> bool:
    """ Function checks if the host is reachable over ICMP. """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)) as sock:
        sock.settimeout(1)
        try:
            sock.connect((str(host), 1))
        except socket.error:
            return False
    return True


def check_port(port: PortNumber, host: IPv4Address, timeout: float = 1) -> bool:
    """ Function checks if the port is open on the provided host. """

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        try:
            if sock.connect_ex((str(host), port)) == 0:
                return True
        except socket.timeout:
            return False
    return False


def ipv4_to_target(ip: IPv4Address, port: PortNumber) -> Target:
    """ Function converts IPv4 address to a Target object """
    return Target(host=str(ip), port=port)


# pylint: disable=unsupported-assignment-operation
UTIL_REGISTRY.generators["hostsFromNetwork"] = get_hosts_for_network
UTIL_REGISTRY.checks["icmpCheck"] = check_host
UTIL_REGISTRY.checks["tcpCheck"] = check_port
UTIL_REGISTRY.producers["ipv4ToTarget"] = ipv4_to_target
