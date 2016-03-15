# kombu v4 will come out with the following commit in:
# https://github.com/celery/kombu/commit/010aae8ccf16ad2fa5a9c3d6f3b84b21e1c1677a
# which does the same thing, but this also allows us to not have to enable
# insecure serializers
import msgpack
from kombu.serialization import register


def pack(s):
    return msgpack.packb(s, use_bin_type=True)


def unpack(s):
    return msgpack.unpackb(s, encoding='utf-8')

register(
    'unicode-msgpack',
    pack,
    unpack,
    content_type='application/x-unicode-msgpack',
    content_encoding='binary'
)
