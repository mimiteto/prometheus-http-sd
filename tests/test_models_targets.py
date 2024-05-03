#! /usr/bin/env python3

"""
Tests for the targets validators
"""


import unittest

from prom_http_sd.models.targets import (
    validate_port, validate_fqdn, target_list_factory,
    Target
)


class TestTarget(unittest.TestCase):
    """ Test the Target class """

    def test_target(self):
        """ Test the Target class """
        target = Target(host="example.com", port=80)
        self.assertEqual(str(target), "example.com:80")


class TestTargetsValidators(unittest.TestCase):
    """ Test the targets validators """

    def test_validate_port(self):
        """ Test the validate_port function """
        self.assertEqual(validate_port(1), 1)
        self.assertEqual(validate_port(65535), 65535)
        with self.assertRaises(ValueError):
            validate_port(0)
        with self.assertRaises(ValueError):
            validate_port(65536)

    def test_validate_fqdn(self):
        """ Test the validate_fqdn function """
        self.assertEqual(validate_fqdn("example.com"), "example.com")
        with self.assertRaises(ValueError):
            validate_fqdn("")
        with self.assertRaises(ValueError):
            validate_fqdn("a" * 254)
        with self.assertRaises(ValueError):
            validate_fqdn("example-.com")
        with self.assertRaises(ValueError):
            validate_fqdn("example.com-")
        with self.assertRaises(ValueError):
            validate_fqdn("example..com")
        with self.assertRaises(ValueError):
            validate_fqdn("example.com..")
        with self.assertRaises(ValueError):
            validate_fqdn("example.com.")
        with self.assertRaises(ValueError):
            validate_fqdn(".example.com")
        with self.assertRaises(ValueError):
            validate_fqdn("-example.com")
        with self.assertRaises(ValueError):
            validate_fqdn('a' * 256)
        with self.assertRaises(ValueError):
            validate_fqdn(f"{'a' * 65}.s")
        with self.assertRaises(ValueError):
            validate_fqdn("a!b.com")


class TestTargetsFactory(unittest.TestCase):
    """ Test the targets factory """

    def test_targets_factory(self):
        """ Test the targets factory """
        def mock_generator_fn() -> list[str]:
            """ Mock the generator function """
            return ["example.com:80", "example.com:443"]

        def check_fn(item: str) -> bool:
            """ Mock the check function """
            return bool(len(item) % 2)

        def producer_fn(item: str) -> Target:
            """ Producer function """
            host, port = item.split(":")
            return Target(host=host, port=int(port))

        with self.subTest("Test the factory"):
            targets = target_list_factory(
                mock_generator_fn, [check_fn], producer_fn
            )
            self.assertEqual(len(targets), 1)
            self.assertEqual(
                targets[0],
                Target(host="example.com", port=443)
            )
