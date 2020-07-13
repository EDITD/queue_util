queue_util
==========
[![Build Status](https://travis-ci.org/EDITD/queue_util.svg?branch=master)](https://travis-ci.org/EDITD/queue_util)
[![Pypi Version](https://img.shields.io/pypi/v/queue_util.svg)](c)
[![Python Versions](https://img.shields.io/pypi/pyversions/queue_util.svg)](https://pypi.org/project/queue_util/)

A set of utilities for consuming (and producing) from a rabbitmq queue


# Development
## Testing
```
tox [-p auto]
```

## Release
* Update [CHANGELOG](CHANGELOG.md) to add new version and document it
* In GitHub, create a new release
  * Name the release `v<version>` (for example `v1.2.3`)
  * Title the release with a highlight of the changes
  * Copy changes in the release from `CHANGELOG.md` into the release description
[TravisCI](https://travis-ci.org/EDITD/queue_util) will package the release and publish it to [Pypi](https://pypi.org/project/queue_util/)
