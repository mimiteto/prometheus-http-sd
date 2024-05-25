#! /usr/bin/env python3

""" Utility functions for Prometheus HTTP Service Discovery """

from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from typing import Any
from functools import partial
from prom_http_sd.models.discovery import DiscoveryResult
from prom_http_sd.models.util_types import (
    Configuration, DiscoveryConf,
    GeneratorFuncType, CheckFuncType, ProducerFuncType
)

from prom_http_sd.models.targets import Target, Targets, TargetsList


def target_list_factory(
    generator_fn: GeneratorFuncType,
    check_fns: list[CheckFuncType],
    producer_fn: ProducerFuncType,
    *args,
    **kwargs
) -> list[Target]:
    """
    Function generates targets based on provided generator function.
    All additional args are passed to the generator function.
    """
    targets: list[Target] = []
    futures: dict[Future, Any] = {}

    def validate(item) -> bool:
        return all(check_fn(host=item) for check_fn in check_fns)

    generated_items = generator_fn(*args, **kwargs)

    with ThreadPoolExecutor(max_workers=len(generated_items)) as executor:
        for item in generated_items:
            try:
                futures[executor.submit(validate, item)] = item
            except RuntimeError:
                break
        for future in as_completed(futures):
            if future.result():
                targets.append(
                    producer_fn(futures[future])
                )
    return targets


def run_discovery(conf: DiscoveryConf) -> list[Targets]:
    """ Start the service discovery """

    return [
        Targets(
            labels=conf.labels,
            targets=target_list_factory(
                conf.generator,
                [
                    partial(
                        c[0], **c[1]
                    ) for c in conf.checks
                ],
                lambda host: conf.producer(host, **conf.producer_args),
                conf.network,
                **conf.generator_args
            )
        )
    ]


def run(conf: Configuration, result_cache: DiscoveryResult) -> None:
    """ Runs service discovery based on confs """
    targets = [run_discovery(disc) for disc in conf.discovery_confs]
    result_cache.set_value(TargetsList(
        targets=[t for sublist in targets for t in sublist]
    ))
