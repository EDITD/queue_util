# kombu v4 will come out with the following commit in:
# https://github.com/celery/kombu/commit/010aae8ccf16ad2fa5a9c3d6f3b84b21e1c1677a
# which does the same thing, but this also allows us to not have to enable
# insecure serializers
from datetime import datetime

import msgpack
import six

from kombu.serialization import register


DATE_FORMAT = "%Y%m%dT%H:%M:%S.%f"
MESSAGE_CONTENT_TYPE = "application/x-unicode-msgpack-with-dates"
MESSAGE_CONTENT_ENCODING = "binary"


def decode_datetime(obj):
    if b"__datetime__" in obj:
        # This must have been produced by python2.
        obj = datetime.strptime(obj[b"as_str"].decode("utf-8"), DATE_FORMAT)
    elif "__datetime__" in obj:
        as_str = obj["as_str"]
        # We are not done yet!! Just because the keys are unicode, doesn't mean that the
        # values are!!
        if six.PY3 and isinstance(as_str, six.binary_type):
            as_str = as_str.decode("utf-8")
        obj = datetime.strptime(as_str, DATE_FORMAT)

    return obj


def encode_datetime(obj):
    if isinstance(obj, datetime):
        # We want to return a dict that can be parsed later.
        # The dict should __always__ have unicode output.

        if six.PY3:
            as_str = obj.strftime(DATE_FORMAT)
        elif six.PY2:
            # We are in python2! But we want to output unicode.unicode_literals will take care
            # of the keys, but strftime returns a bytestring in python2.
            as_bytes = obj.strftime(DATE_FORMAT)
            as_str = as_bytes.decode("utf-8")
        return {"__datetime__": True, "as_str": as_str}

    return obj


def pack(s):
    return msgpack.packb(
        s,
        use_bin_type=True,
        unicode_errors="ignore",
        default=encode_datetime,
    )


def unpack(s):
    return msgpack.unpackb(
        s,
        encoding="utf-8",
        unicode_errors="ignore",
        object_hook=decode_datetime,
    )


register(
    "unicode-msgpack-with-dates",
    pack,
    unpack,
    content_type=MESSAGE_CONTENT_TYPE,
    content_encoding=MESSAGE_CONTENT_ENCODING,
)

# This is around for compatibility reasons (so that we're able to decode any messages
# that are already in queues, with the old/non-date-aware content_type).
register(
    'unicode-msgpack',
    pack,
    unpack,
    content_type='application/x-unicode-msgpack',
    content_encoding='binary'
)
