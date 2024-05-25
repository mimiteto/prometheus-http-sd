#! /usr/bin/env python3

"""
Type definitions for SD util functions.
Use the UTIL_REGISTRY to register util functions.
"""

from ipaddress import IPv4Network, ip_network
from typing import Annotated, Any, Callable, TypeVar
from pydantic import (
    BaseModel, Field, AfterValidator, PositiveInt, ConfigDict
)
from prom_http_sd.models.targets import Target, PortNumber, FQDN


T = TypeVar("T")
GeneratorFuncType = Callable[..., list[T]]
CheckFuncType = Callable[[T], bool]
ProducerFuncType = Callable[[T], Target]


class UtilRegistry(BaseModel):
    """ Registry for util functions """
    generators: dict[str, GeneratorFuncType] = Field(default_factory=dict)
    checks: dict[str, CheckFuncType] = Field(default_factory=dict)
    producers: dict[str, ProducerFuncType] = Field(default_factory=dict)

    def _get_util(
        self, name: str, util_dict: dict[str, T], util_type: str
    ) -> T:
        """ Get util function by name """
        try:
            return util_dict[name]
        except KeyError as err:
            raise ValueError(f"{util_type} {name} not found") from err

    def get_generator(self, name: str) -> GeneratorFuncType:
        """ Get generator function by name """
        return self._get_util(name, self.generators, "Generator")

    def get_check(self, name: str) -> CheckFuncType:
        """ Get check function by name """
        return self._get_util(name, self.checks, "Check")

    def get_producer(self, name: str) -> ProducerFuncType:
        """ Get producer function by name """
        return self._get_util(name, self.producers, "Producer")


def validate_ipv4_network_str(net: str):
    """ Validate if the string is a valid IPv4 network """
    if not isinstance(ip_network(net, strict=False), IPv4Network):
        raise ValueError(f"{net} is not a valid IPv4 network")
    return net


UTIL_REGISTRY = UtilRegistry()

Generator = Annotated[
    str, AfterValidator(UTIL_REGISTRY.get_generator)
]

Check = Annotated[
    str, AfterValidator(UTIL_REGISTRY.get_check)
]

Producer = Annotated[
    str, AfterValidator(UTIL_REGISTRY.get_producer)
]

IPv4NetworkStr = Annotated[str, AfterValidator(validate_ipv4_network_str)]

ChecksTuple = tuple[Check, dict[str, Any]]


class DiscoveryConf(BaseModel):
    """ Configuration for the app """

    model_config = ConfigDict(
        title="Target discovery definition",
    )
    network: IPv4NetworkStr | FQDN
    generator: Generator
    generator_args: dict[str, Any] = Field(default_factory=dict)
    checks: list[ChecksTuple]
    producer: Producer
    producer_args: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)


class Configuration(BaseModel):
    """ Prom HTTP SD Configuration """
    model_config = ConfigDict(
        title="Prometheus HTTP Service Discovery Configuration"
    )
    port: PortNumber = 8765
    frequency: PositiveInt = 10
    discovery_confs: list[DiscoveryConf]
