queue_util
==========

A set of utilities for consuming (and producing) from a rabbitmq queue


### Releasing a new version

* It's a package (`http://packages.edtd.net/queue_util-${version}.tar.gz`)
* Do a `git flow release` and make sure you update the version number in `setup.py`.
* Run `curl -X POST http://packages.edtd.net/ensure/github/EDITD/queue_util` to build the latest tag automatically (more about this on http://packages.edtd.net)
* Tell interested people that your new version is available.
