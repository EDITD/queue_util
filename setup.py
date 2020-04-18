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
        name='queue_util',
        version=get_version(),
        author='EDITED devs',
        author_email='dev@edited.com',
        packages=setuptools.find_packages(),
        scripts=[],
        url='https://github.com/EDITD/queue_util',
        license='file: LICENSE.txt',
        description='A set of utilities for consuming (and producing) from a rabbitmq queue',
        long_description='file: README.md',
        long_description_content_type='text/markdown',
        install_requires=REQUIREMENTS,
        extras_require={
            'dev': (
                'tox>=3.14.0',
                'docker>=4.1.0,<4.2',
            ),
        },
        python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Intended Audience :: Information Technology',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Topic :: Software Development :: Libraries :: Application Frameworks',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
