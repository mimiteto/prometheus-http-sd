#! /usr/bin/env python3

""" Main module for the prom_http_sd package """

import sys
from pprint import pprint

import prom_http_sd.pkgs.ip_networks as net
import prom_http_sd.models.targets as t


def main(nlen: str) -> None:
    """ Main function """
    network = f"172.17.0.0/{nlen}"
    port: t.PortNumber = 80

    targets: t.TargetsList = t.TargetsList(
        targets=[
            t.Targets(
                labels={},
                targets=t.target_list_factory(
                    net.get_hosts_for_network,
                    # [net.check_host, check_port_8080],
                    [
                        net.check_host,
                        lambda host: net.check_port(port, host)
                    ],
                    # ipv4_to_target_with_port_8080,
                    lambda ip: net.ipv4_to_target(ip, port),
                    network
                )
            )
        ]
    )
    pprint(targets)


if __name__ == "__main__":
    network_len = sys.argv[1] if len(sys.argv) > 1 else "24"
    print(f"Running main with {network_len}")
    main(network_len)
