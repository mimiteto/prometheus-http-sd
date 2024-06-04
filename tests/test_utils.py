#! /usr/bin/env python3

""" Test the utils module """


import unittest

from prom_http_sd.models.discovery import DiscoveryResult
from prom_http_sd.models.targets import Target, Targets, TargetsList
import prom_http_sd.models.util_types as ut
from prom_http_sd import utils


class TestTargetListFactory(unittest.TestCase):
    """ Test the target_list_factory function """

    def test_target_list_factory(self):
        """ Test the target_list_factory function """
        def gen(*_, **__):
            """ Mock generator """
            return [{'host': '0.0.0.0', 'port': 8080}, {'host': '1.1.1.1', 'port': 8080}]

        def check(*_, **__):
            """ Mock check """
            return True

        self.assertListEqual(
            utils.target_list_factory(
                gen,
                [check],
                lambda x: Target(**x)
            ),
            [Target(host='0.0.0.0', port=8080), Target(host='1.1.1.1', port=8080)]
        )

    def test_target_list_factory_with_failed_check(self):
        """ Test the target_list_factory function with invalid input """
        val = 1

        def gen(*_, **__):
            """ Mock generator """
            return [{'host': '0.0.0.0', 'port': 8080}, {'host': '1.1.1.1', 'port': 8080}]

        def check(*_, **__):
            """ Mock check """
            nonlocal val
            val += 1
            return bool(val % 2)

        self.assertListEqual(
            utils.target_list_factory(
                gen,
                [check],
                lambda x: Target(**x)
            ),
            [Target(host='1.1.1.1', port=8080)]
        )


class TestRunDiscovery(unittest.TestCase):
    """ Test the run_discovery function """

    def test_basic_conf(self):
        """ Test the run_discovery function """
        # pylint: disable=unsupported-assignment-operation
        ut.UTIL_REGISTRY.generators["basic"] = lambda _: [{'host': '0.0.0.0', 'port': 8080}]
        # pylint: disable=unnecessary-lambda
        ut.UTIL_REGISTRY.checks["basic"] = lambda host: bool(host)
        ut.UTIL_REGISTRY.producers["basic"] = lambda x: Target(**x)

        self.assertListEqual(
            utils.run_discovery(ut.DiscoveryConf(
                network='1.2.3.4/32',
                generator='basic',
                checks=[('basic', {})],
                producer='basic',
            )),
            [Targets(
                labels={},
                targets=[Target(host='0.0.0.0', port=8080)],
            )]
        )

    def test_discovery_with_args(self):
        """ Test the run_discovery function with args """
        def gen(_, h, p):
            """ Mock generator """
            return [{'host': h, 'port': p}]

        # pylint: disable=unused-argument
        def check(host, arg):
            """ Mock check """
            return bool(arg)

        # pylint: disable=unused-argument
        def prod(x, res):
            """ Mock producer """
            return res

        # pylint: disable=unsupported-assignment-operation
        ut.UTIL_REGISTRY.generators["args"] = gen
        ut.UTIL_REGISTRY.checks["args"] = check
        ut.UTIL_REGISTRY.producers["args"] = prod

        self.assertListEqual(
            utils.run_discovery(ut.DiscoveryConf(
                network='1.2.3.4/24',
                generator='args',
                generator_args={'h': '1.1.1.1', 'p': 8080},
                checks=[('args', {'arg': True})],
                producer='args',
                producer_args={'res': Target(host='2.2.2.2', port=9999)}
            )),
            [Targets(
                labels={},
                targets=[Target(host='2.2.2.2', port=9999)]
            )]
        )


class TestRun(unittest.TestCase):
    """ Test the run function """

    def test_run_with_empty_discovery(self):
        """ Test the run function with empty discovery """
        res = DiscoveryResult()
        utils.run(
            utils.Configuration(frequency=10, discovery_confs=[]),
            res
        )

        self.assertEqual(
            res.get_value(),
            TargetsList(targets=[])
        )

    def test_run_with_discovery(self):
        """ Test the run function with discovery """
        def gen(_, h, p):
            """ Mock generator """
            return [{'host': h, 'port': p}]

        # pylint: disable=unused-argument
        def check(host, arg):
            """ Mock check """
            return bool(arg)

        # pylint: disable=unused-argument
        def prod(x, res):
            """ Mock producer """
            return res

        # pylint: disable=unsupported-assignment-operation
        ut.UTIL_REGISTRY.generators["args"] = gen
        ut.UTIL_REGISTRY.checks["args"] = check
        ut.UTIL_REGISTRY.producers["args"] = prod

        res = DiscoveryResult()
        utils.run(
            utils.Configuration(
                frequency=10,
                discovery_confs=[ut.DiscoveryConf(
                    network='1.2.3.4/24',
                    generator='args',
                    generator_args={'h': '1.1.1.1', 'p': 8080},
                    checks=[('args', {'arg': True})],
                    producer='args',
                    producer_args={'res': Target(host='2.2.2.2', port=9999)}
                )]
            ),
            res
        )

        self.assertEqual(
            res.get_value(),
            TargetsList(
                targets=[Targets(
                    labels={},
                    targets=[Target(host='2.2.2.2', port=9999)]
                )]
            )
        )
