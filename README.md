queue_util
==========
[![Build Status](https://travis-ci.org/EDITD/queue_util.svg?branch=master)](https://travis-ci.org/EDITD/queue_util)
[![Pypi Version](https://img.shields.io/pypi/v/queue_util.svg)](https://pypi.org/project/queue_util/)
[![Python Versions](https://img.shields.io/pypi/pyversions/queue_util.svg)](https://pypi.org/project/queue_util/)

A set of utilities for consuming (and producing) from a rabbitmq queue

# End of life
This project is not actively developed any more.

Kombu has provided the ConsumerMixin utility for a very long time now. That abstraction allows to
code Consumers very similar to the one provided here with very little code, and much better
handling of errors, disconnections and the full range of features that Kombu has on offer.

If you are still actively using this library and need support for it, please get in touch
with a GitHub issue or an email.

# Development
## Testing
You will need to have:
* a local `Docker` service
* `tox` installed (globally available)
* All supported versions of python installed ([Pyenv](https://github.com/pyenv/pyenv) is highly
 recommended)
```
tox [-p auto]
```

## Release
* Update [CHANGELOG](CHANGELOG.md) to add new version and document it
* In GitHub, create a new release
  * Name the release `v<version>` (for example `v1.2.3`)
  * Title the release with a highlight of the changes
  * Copy changes in the release from `CHANGELOG.md` into the release description
 [TravisCI](https://travis-ci.org/EDITD/queue_util) will package the release and publish it to
 [Pypi](https://pypi.org/project/queue_util/)
