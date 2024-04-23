#! /usr/bin/env python3

"""
This module defines the data models for the Prometheus HTTP Service Discovery.
"""

import re
from typing import Annotated
from pydantic import BaseModel, PositiveInt
from pydantic.functional_validators import AfterValidator
from pydantic.networks import IPvAnyAddress


def validate_port(port: PositiveInt) -> PositiveInt:
    """ Function asserts that port number is valid """
    if port < 1 or port > 65535:
        raise ValueError("Port number must be between 1 and 65535")
    return port


def validate_fqdn(fqdn: str) -> str:
    """ Function asserts that FQDN is valid """
    def validate_chunk(chunk: str) -> str:
        if len(chunk) < 1:
            raise ValueError("FQDN chunk must not be empty")
        if len(chunk) > 63:
            raise ValueError("FQDN chunk must not be longer than 63 characters")
        if not re.match(r"^[a-z0-9-]+$", chunk):
            raise ValueError("FQDN chunk must match the regex '^[a-z0-9-]+$'")
        if chunk[0] == '-' or chunk[-1] == '-':
            raise ValueError("FQDN chunk must not start or end with a hyphen")
        return chunk
    if len(fqdn) < 1:
        raise ValueError("FQDN must not be empty")
    if len(fqdn) > 253:
        raise ValueError("FQDN must not be longer than 253 characters")
    _ = [validate_chunk(chunk) for chunk in fqdn.split('.')]
    return fqdn


PortNumber = Annotated[PositiveInt, AfterValidator(validate_port)]
FQDN = Annotated[str, AfterValidator(validate_fqdn)]


class Target(BaseModel):
    """ Target Description """
    host: IPvAnyAddress | FQDN
    port: PositiveInt

    def __str__(self):
        return f"{self.host}:{self.port}"


class Targets(BaseModel):
    """ Targets Description """
    labels: dict[str, str]
    targets: list[Target]


class TargetsList(BaseModel):
    """ List of Targets """
    targets: list[Targets]
