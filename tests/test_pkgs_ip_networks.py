#! /usr/bin/env python3

""" Tests for ip_networks module """

import unittest
from unittest.mock import patch, MagicMock

import socket
from ipaddress import IPv4Address

import prom_http_sd.pkgs.ip_networks as nets
from prom_http_sd.models.targets import Target


class TestIpNetworks(unittest.TestCase):
    """ Test the ip_networks module """

    def test_get_hosts_for_network(self):
        """ Test the get_hosts_for_network function """
        self.assertEqual(
            nets.get_hosts_for_network("172.16.0.0/32"),
            [IPv4Address("172.16.0.0")]
        )
        self.assertEqual(
            nets.get_hosts_for_network("172.16.0.3/26"),
            [IPv4Address(f"172.16.0.{last_octet}") for last_octet in range(1, 63)]
        )
        with self.assertRaises(NotImplementedError):
            nets.get_hosts_for_network("2001:db8::/32")

    @patch("prom_http_sd.pkgs.ip_networks.socket.socket")
    def test_check_host(self, mock_socket):
        """ Test the check_host function """
        mock_socket.return_value = MagicMock()
        mock_socket.return_value.connect = MagicMock(
            side_effect=[None, socket.error]
        )
        self.assertTrue(nets.check_host("host"))
        self.assertFalse(nets.check_host("host"))

    @patch("prom_http_sd.pkgs.ip_networks.socket.socket")
    def test_check_port(self, mock_socket):
        """ Test the check_port function """
        mock_socket.return_value = MagicMock()
        mock_socket.return_value.connect_ex = MagicMock(
            side_effect=[0, 1, socket.timeout]
        )
        self.assertTrue(nets.check_port(80, "host"))
        self.assertFalse(nets.check_port(80, "host"))
        self.assertFalse(nets.check_port(80, "host"))

    def test_ipv4_to_target(self):
        """ Test the ipv4_to_target function """
        self.assertEqual(
            nets.ipv4_to_target(
                IPv4Address("172.16.0.1"), 80
            ),
            Target(host="172.16.0.1", port=80)
        )
