# Changelog
### Unreleased - leave this line in when you do a release, and leave 1 blank line underneath what you release

## v3.0.1
- Update meta information
- Add labels in README
- Migrate to TravisCI for build and release

## v3.0.0
- Upgrade to Kombu 4, msgpack 0.5, statsd 3
- Use tox for testing with multiple Python versions
- Add integration tests

## v2.2.1
- Update `unicode-msgpack` serialiser to date-aware implementation
- Ignore unicode_errors on read and write with `unicode-msgpack`

## v2.2.0
- Allow specification of `userid` and `password` when connecting

## v2.1.1
- Fix `msgpack-python` dependency

## v2.1.0
- Add the `unicode-msgpack` serializer and make msgpack a dependency

## v2.0.1
- fix bug with the order of specifying serializer and compression per new item

## v2.0.0
- allow users of queue_util to specify serializer and compression per new message
- [breaking] Update kombu to a version that supports Python 3.4

## v1.0.1
- Fix setup.py for Python 3

## v1.0.0
- Support Python 2 & 3 via six
