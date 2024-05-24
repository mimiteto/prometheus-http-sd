#! /usr/bin/env python3

""" Module provides discovery model and utils """

import logging
from threading import Lock

from prom_http_sd.models.targets import TargetsList


class DiscoveryResult:
    """ Model for discovery result """

    def __init__(self, logger: logging.Logger | None = None):
        self._lock = Lock()
        self._last_value: TargetsList | None = None
        self._log = logger or logging.getLogger(self.__class__.__name__)

    def get_value(self) -> TargetsList:
        """ Get last value from cache. Raises ValueError if cache is empty """
        with self._lock:
            if self._last_value is not None:
                self._log.debug("Returning value from cache - %s", self._last_value)
                return self._last_value
        self._log.info("Hitting empty cache")
        raise ValueError("Hitting empty cache")

    def set_value(self, value: TargetsList):
        """ Set new value to cache """
        with self._lock:
            self._log.debug("Setting new value to cache - %s", value)
            self._last_value = value


RESULT_CACHE = DiscoveryResult()
