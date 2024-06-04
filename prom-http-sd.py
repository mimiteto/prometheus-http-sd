#! /usr/bin/env python3
# pylint: disable=invalid-name,fixme

"""
Executable for the prom_http_sd package
"""


import sys
from time import sleep
from contextlib import asynccontextmanager
from threading import Thread
from typing import Callable

from ruamel.yaml import YAML
from fastapi import FastAPI, HTTPException

import prom_http_sd.models.util_types as ut
import prom_http_sd.utils as u

# TODO: Correct tests
# TODO: Make all utils loadable as prom_http_sd.*
# TODO: Add posibility to load modules


from prom_http_sd.models.discovery import (
    DiscoveryResult,
    RESULT_CACHE
)


def loop(exc: Callable, wait: int | None = None):
    """ Loops the given function """
    while True:
        exc()
        if wait is not None:
            sleep(wait)


def gen_discovery(conf: ut.Configuration, cache: DiscoveryResult) -> Thread:
    """ Generate the discovery thread """
    return Thread(
        target=loop,
        args=(
            lambda: u.run(conf, cache),
            conf.frequency
        )
    )


# pylint: disable=unused-argument
@asynccontextmanager
async def lifecycle(application: FastAPI):
    """ Context manager for the FastAPI app """
    yield
    sys.exit(0)


with open("resources/default-conf.yaml", "r", encoding="utf-8") as file:
    configuration = ut.Configuration(**YAML().load(file))


app = FastAPI(
    title="Prometheus HTTP Service Discovery",
    description="Service discovery for Prometheus",
    lifecycle=lifecycle
)
discovery_thread = gen_discovery(configuration, RESULT_CACHE)


@app.get("/discovery")
async def get_discovery() -> u.TargetsList:
    """ Get discovered entities """
    try:
        return RESULT_CACHE.get_value()
    except ValueError as exc:
        raise HTTPException(
            status_code=503, detail=f"Failed to get discovery cache - {exc}"
        ) from exc


discovery_thread.start()
