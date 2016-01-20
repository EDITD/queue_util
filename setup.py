import setuptools


# How do we keep this in sync with requirements.pip?
#
REQUIREMENTS = [
    "kombu>=2.5,<2.6",
    "nose>=1.3,<1.4",
    "requests>=2,<3",
    "statsd>=2.1,<2.2",
]


if __name__ == "__main__":
    setuptools.setup(
        name="queue_util",
        version="0.0.11",
        author="Sujay Mansingh",
        author_email="sujay.mansingh@gmail.com",
        packages=setuptools.find_packages(),
        scripts=[],
        url="https://github.com/sujaymansingh/queue_util",
        license="LICENSE.txt",
        description="A set of utilities for consuming (and producing) from a rabbitmq queue",
        long_description="View the github page (https://github.com/sujaymansingh/queue_util) for more details.",
        install_requires=REQUIREMENTS
    )
