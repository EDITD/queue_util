#! env python

import contextlib
import os
import sys

import docker

from . import app

RABBIT_IMAGE = "rabbitmq:3.8.2-management-alpine"
RABBIT_NAME = "rabbitmq_queue_utils_test_app_{}".format(os.getpid())


@contextlib.contextmanager
def rabbitmq_test_server():
    client = docker.from_env()

    exposed_ports = ["{0}/tcp".format(port) for port in (5672, 15672)]
    container = None
    try:
        container = client.containers.run(
            RABBIT_IMAGE,
            remove=True,
            detach=True,
            ports={port: None for port in exposed_ports},
            name=RABBIT_NAME,
        )
        # The docker-py API is not great to get the host port
        # See https://github.com/docker/docker-py/issues/1451
        host_ports = client.api.inspect_container(container.id)["NetworkSettings"]["Ports"]
        yield [int(host_ports[port][0]['HostPort']) for port in exposed_ports]
    finally:
        if container is not None:
            container.remove(force=True)


def main():
    RABBIT_HOST = '127.0.0.1'
    RABBIT_QUEUE_NAME = 'queue_util_test_app'

    with rabbitmq_test_server() as rabbit_ports:
        return app.main(RABBIT_QUEUE_NAME, rabbit_host=RABBIT_HOST, rabbit_port=rabbit_ports[0])


if __name__ == '__main__':
    sys.exit(main())
