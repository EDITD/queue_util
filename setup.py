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
    changelog_file = "CHANGELOG.md"
    with open(changelog_file, "r") as changelog:
        for changelog_line in changelog:
            version = version_pattern.search(changelog_line)
            if version is not None:
                return "".join(version.group())
        raise RuntimeError("Couldn't find a valid version in {}".format(changelog_file))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "requirements":
        for req in REQUIREMENTS:
            print(req)
        sys.exit(0)

    setuptools.setup(
        name="queue_util",
        version=get_version(),
        author='EDITED devs',
        author_email='dev@edited.com',
        packages=setuptools.find_packages(),
        scripts=[],
        url="https://github.com/EDITD/queue_util",
        license="LICENSE.txt",
        description="A set of utilities for consuming (and producing) from a rabbitmq queue",
        long_description="View the github page (https://github.com/EDITD/queue_util) for more details.",
        install_requires=REQUIREMENTS,
        extras_require={
            'dev': (
                'tox>=3.14.0',
                'docker>=4.1.0,<4.2',
            ),
        },
    )
