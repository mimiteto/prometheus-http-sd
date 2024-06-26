#! /usr/bin/env python3

"""
This module defines the data models for the Prometheus HTTP Service Discovery.
"""

import re
from typing import Annotated, Callable, TypeVar
from concurrent.futures import ThreadPoolExecutor, Future, as_completed

from pydantic import BaseModel, PositiveInt
from pydantic.functional_validators import AfterValidator
from pydantic.networks import IPvAnyAddress

T = TypeVar("T")


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


def target_list_factory(
    generator_fn: Callable[..., list[T]],
    check_fns: list[Callable[[T], bool]],
    producer_fn: Callable[[T], Target],
    *args,
    **kwargs
) -> list[Target]:
    """
    Function generates targets based on provided generator function.
    All additional args are passed to the generator function.
    """
    targets: list[Target] = []
    futures: dict[Future, T] = {}

    def validate(item) -> bool:
        return all(check_fn(item) for check_fn in check_fns)

    generated_items = generator_fn(*args, **kwargs)
    with ThreadPoolExecutor(max_workers=len(generated_items)) as executor:
        for item in generated_items:
            futures[executor.submit(validate, item)] = item
        for future in as_completed(futures):
            if future.result():
                targets.append(
                    producer_fn(futures[future])
                )
    return targets
