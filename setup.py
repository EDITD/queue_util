import re
import setuptools
import sys


REQUIREMENTS = [
    "kombu>=4.5.0,<4.6",
    "six>=1.14.0,<2",
    "msgpack-python>=0.5.6,<0.6",
    "statsd>=3.3.0,<4",
]

# Regex matching version pattern
# (3 numerical values separated by `.`, semver style, followed by an optional pre-release marker)
version_pattern = re.compile(r"\d+\.\d+\.\d+([.-][\w_-]+)?")


def get_version():
    with open("CHANGELOG.md", "r") as fn:
        while True:
            version = version_pattern.search(fn.readline())
            if version is not None:
                return "".join(version.group())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "requirements":
        for req in REQUIREMENTS:
            print(req)
        sys.exit(0)

    setuptools.setup(
        name="queue_util",
        version=get_version(),
        author="Sujay Mansingh",
        author_email="sujay.mansingh@gmail.com",
        packages=setuptools.find_packages(),
        scripts=[],
        url="https://github.com/sujaymansingh/queue_util",
        license="LICENSE.txt",
        description="A set of utilities for consuming (and producing) from a rabbitmq queue",
        long_description="View the github page (https://github.com/sujaymansingh/queue_util) for more details.",
        install_requires=REQUIREMENTS,
        extras_require={
            'fast': (
                "librabbitmq>=2.0.0,<3",
            ),
            'dev': (
                'tox>=3.14.0',
                'docker>=4.1.0,<4.2',
            ),
        },
    )
