#! /usr/bin/env python3

"""
Module provides tests for the discovery module
"""

import unittest

from prom_http_sd.models.discovery import DiscoveryResult
from prom_http_sd.models.targets import TargetsList


class TestDiscoveryResult(unittest.TestCase):
    """ Test the DiscoveryResult class """

    def test_get_value(self):
        """ Test the get_value method """
        result = DiscoveryResult()
        with self.assertRaises(ValueError):
            result.get_value()

    def test_set_value(self):
        """ Test the set_value method """
        result = DiscoveryResult()
        t = TargetsList(targets=[])
        result.set_value(t)
        self.assertEqual(result.get_value(), t)
