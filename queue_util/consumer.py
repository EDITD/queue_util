"""Listens to 1 (just one!) queue and consumes messages from it endlessly.
We set up a consumer with two things:
1) The name of the source queue (`source_queue_name`)
2) A callable that will process

The `handle_data` method must process the data. It can return nothing or a
sequence of `queue_name, data` pairs.
If it returns the latter, then the data will be sent to the given `queue_name`.
e.g.

def handle_data(data):
    new_data = do_some_calc(data)

    # Forward the new_data to another queue.
    #
    yield ("next_target", new_data)
"""
import logging

import kombu



class Consumer(object):

    def __init__(self, source_queue_name, handle_data, rabbitmq_host, serializer=None, compression=None):
        self.serializer = serializer
        self.compression = compression
        self.queue_cache = {}

        # Connect to the source queue.
        #
        self.broker = kombu.BrokerConnection(rabbitmq_host)
        self.source_queue = self.get_queue(source_queue_name, serializer=serializer, compression=compression)

        # The handle_data method will be applied to each item in the queue. 
        #
        self.handle_data = handle_data

    def get_queue(self, queue_name, serializer=None, compression=None):
        kwargs = {}

        # Use 'defaults' if no args were supplied for serializer/compression.
        #
        serializer = serializer or self.serializer
        if serializer:
            kwargs["serializer"] = serializer

        compression = compression or self.compression
        if compression:
            kwargs["compression"] = compression

        # The cache key is the name and connection args.
        # This is so that (if needed) a fresh connection can be made with
        # different serializer/compression args.
        #
        cache_key = (queue_name, serializer, compression,)
        if cache_key not in self.queue_cache:
            self.queue_cache[cache_key] = self.broker.SimpleQueue(queue_name, **kwargs)
        return self.queue_cache[cache_key]

    def run_forever(self):
        """Keep running (unless we get a Ctrl-C).
        """
        while True:
            try:
                message = self.source_queue.get(block=True)
                data = message.payload

                new_messages = self.handle_data(data)

            except KeyboardInterrupt:
                logging.info("Caught Ctrl-C. Byee!")
                # Break out of our loop.
                #
                break
            else:
                # Queue up the new messages (if any).
                #
                if new_messages:
                    for queue_name, data in new_messages:
                        destination_queue = self.get_destination_queues(queue_name)
                        destination_queue.put(data)

                # We're done with the original message.
                #
                message.ack()
