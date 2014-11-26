queue_util
==========

A set of utilities for consuming (and producing) from a rabbitmq queue


### Releasing a new version

* It's a package (`http://packages.edtd.net/queue_util-${version}.tar.gz`)
* Update the version number in `setup.py` and make a new tag/release (e.g. via the github release interface)
* Run `curl -X POST http://packages.edtd.net/ensure/github/EDITD/queue_util` to build the latest tag automatically (more about this on http://packages.edtd.net)
* Tell interested people that your new version is available.
