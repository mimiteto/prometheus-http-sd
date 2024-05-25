#! /usr/bin/env python3

""" Main module for the prom_http_sd package """

from time import sleep

from threading import Thread
from typing import Callable
from pydantic import BaseModel, PositiveInt, ConfigDict
import prom_http_sd.pkgs.ip_networks as net
import prom_http_sd.models.targets as t
import prom_http_sd.models.util_types as ut
import prom_http_sd.utils as u
import prom_http_sd.pkgs.ip_networks as net

# pylint: disable=unused-import
from prom_http_sd.api.discovery import app  # noqa: F401
from prom_http_sd.models.discovery import RESULT_CACHE


def loop(exc: Callable, wait: int | None = None):
    """ Loops the given function """
    while True:
        exc()
        if wait is not None:
            sleep(wait)


conf = ut.Configuration(
    discovery_confs=[
        ut.DiscoveryConf(
            labels={"job": "test"},
            generator="hostsFromNetwork",
            checks=[
                ("icmpCheck", {}),
                ("tcpCheck", {"port": 80}),
            ],
            producer="ipv4ToTarget",
            producer_args={"port": 80},
            network='172.17.0.0/26'
        )
    ]
)

discovery_thread = Thread(
    target=loop,
    args=(
        lambda: u.run(conf, RESULT_CACHE),
        conf.frequency
    )
)

discovery_thread.start()
