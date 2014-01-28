"""Allow the ability to connect and publish to a queue.
"""
import kombu


class Producer(object):

    def __init__(self, dest_queue_name, rabbitmq_host, serializer=None, compression=None):
        self.serializer = serializer
        self.compression = compression
        self.queue_cache = {}

        # Connect to the queue.
        #
        broker = kombu.BrokerConnection(rabbitmq_host)
        self.dest_queue = broker.SimpleQueue(dest_queue_name, serializer=serializer, compression=compression)

    def put(self, item):
        """Put one item onto the queue.
        """
        self.dest_queue.put(item)
