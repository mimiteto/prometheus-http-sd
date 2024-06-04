#! /usr/bin/env python3

""" Tests for the util types """

import unittest

from prom_http_sd.models.targets import Target
from prom_http_sd.models.util_types import (
    UtilRegistry, validate_ipv4_network_str
)


class TestValidateIPv4Networkstr(unittest.TestCase):
    """ Test the validate_ipv4_network_str function """

    def test_validate_ipv4_network_str(self):
        """ Test the validate_ipv4_network_str function """
        self.assertEqual(
            validate_ipv4_network_str("1.2.3.4/32"),
            "1.2.3.4/32"
        )

    def test_validate_ipv4_network_str_invalid(self):
        """ Test the validate_ipv4_network_str function with invalid input """
        with self.assertRaises(ValueError):
            validate_ipv4_network_str("abv.bg")

        with self.assertRaises(ValueError):
            validate_ipv4_network_str("1234::/32")


class TestUtilRegistry(unittest.TestCase):
    """ Test the UtilRegistry class """

    def test_get_generator(self):
        """ Test the get_generator method """
        def gen():
            return []
        registry = UtilRegistry(
            generators={"gen": gen}
        )
        self.assertEqual(registry.get_generator("gen"), gen)
        with self.assertRaises(ValueError):
            registry.get_generator("not_gen")

    def test_get_check(self):
        """ Test the get_check method """
        registry = UtilRegistry(
            checks={"check": lambda: True}
        )
        self.assertTrue(registry.get_check("check"))
        with self.assertRaises(ValueError):
            registry.get_check("not_check")

    def test_get_producer(self):
        """ Test the get_producer method """
        registry = UtilRegistry(
            producers={"prod": Target}
        )
        self.assertEqual(registry.get_producer("prod"), Target)
        with self.assertRaises(ValueError):
            registry.get_producer("not_prod")
