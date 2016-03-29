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

If used with run_forever, handle_data is called once per message.
i.e.
    self.handle_data(message.payload)

If used with batched_run_forever, handle_data is called with a list of payloads
i.e.
    self.handle_data([message.payload for message in current_batch])
"""
import logging
import os
import socket
import time

import kombu
import statsd

from queue_util import stats
from six.moves import queue


class Consumer(object):

    def __init__(self, source_queue_name, handle_data, rabbitmq_host,
                 serializer=None, compression=None, pause_delay=5,
                 statsd_host=None, statsd_prefix="queue_util", workerid=None, worker_id=None,
                 dont_requeue=None, reject=None, handle_exception=None,
                 userid=None, password=None):
        self.serializer = serializer
        self.compression = compression
        self.queue_cache = {}

        self.pause_delay = pause_delay

        # Connect to the source queue.
        connect_kwargs = {}
        if userid is not None:
            connect_kwargs["userid"] = userid
        if password is not None:
            connect_kwargs["password"] = password
        self.broker = kombu.BrokerConnection(rabbitmq_host, **connect_kwargs)
        self.source_queue = self.get_queue(source_queue_name, serializer=serializer, compression=compression)

        # The handle_data method will be applied to each item in the queue.
        #
        self.handle_data = handle_data

        self.workerid = worker_id or workerid

        # If both True, requeue takes priority
        self.requeue = False if dont_requeue else True
        self.reject = True if reject else False

        self.handle_exception = handle_exception

        if statsd_host:
            prefix = self.get_full_statsd_prefix(statsd_prefix, source_queue_name)
            self.statsd_client = statsd.StatsClient(statsd_host, prefix=prefix)
        else:
            self.statsd_client = None

    def get_queue(self, queue_name, serializer="default", compression="default"):
        kwargs = {}

        # Use 'defaults' if no args were supplied for serializer/compression.
        #
        serializer = self.serializer if serializer == "default" else serializer
        if serializer:
            kwargs["serializer"] = serializer

        compression = self.compression if compression == "default" else compression
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

    def post_handle_data(self):
        """This gets called after each item has been processed.
        """
        pass

    def is_paused(self):
        """Return True if the Consumer should be paused. This is checked before
        *every* handle item (and repeatedly if the consumer is paused), so if
        a custom is_pause is provided then don't make it expensive!
        """
        # A default consumer never pauses.
        #
        return False

    def queue_new_messages(self, new_messages):
        for new_message in new_messages:
            new_message_length = len(new_message)

            compression = "default"
            serializer = "default"

            if new_message_length == 4:
                queue_name, data, serializer, compression = new_message
            elif new_message_length == 3:
                queue_name, data, serializer = new_message
            elif new_message_length == 2:
                queue_name, data = new_message
            else:
                raise ValueError(
                    "Expected (queue_name, data(, serializer, compression)) but got {}".format(new_message)
                )

            destination_queue = self.get_queue(queue_name, serializer, compression)
            destination_queue.put(data)

    def run_forever(self):
        """Keep running (unless we get a Ctrl-C).
        """
        while True:
            message = None
            try:
                self.wait_if_paused()

                message = self.source_queue.get(block=True)
                data = message.payload

                with stats.time_block(self.statsd_client):
                    new_messages = self.handle_data(data)

                # Must be successful if we have reached here.
                stats.mark_successful_job(self.statsd_client)

                self.post_handle_data()

            except KeyboardInterrupt:
                logging.info("Caught Ctrl-C. Byee!")
                # Break out of our loop.
                #
                break

            except:
                # Keep going, but don't ack the message.
                # Also, log the exception.
                logging.exception("Exception handling data")

                if self.handle_exception is not None:
                    self.handle_exception()

                if message:
                    if self.requeue:
                        message.requeue()
                    elif self.reject:
                        message.reject()

                stats.mark_failed_job(self.statsd_client)

            else:
                # Queue up the new messages (if any).
                #
                if new_messages:
                    self.queue_new_messages(new_messages)

                # We're done with the original message.
                #
                message.ack()

    def batched_run_forever(self, size, wait_timeout_seconds=5):
        """This will take messages off the queue and put them in a buffer.
        Once the buffer reaches the given size, handle_data is called for the
        entire buffer. (So handle_data must be able to handle a list.)
        If handle_data doesn't throw an exception, all messages are ack'd.
        Otherwise all messages are requeued/rejected.
        """
        buffer = []

        while True:
            new_messages = []
            try:
                self.wait_if_paused()

                queue_was_empty = False
                message = None

                try:
                    # We need to have a timeout. Otherwise if we had no more
                    # messages coming in, but len(buffer) < size, then the
                    # buffer would never get processed!
                    message = self.source_queue.get(block=True, timeout=wait_timeout_seconds)
                except queue.Empty:
                    queue_was_empty = True

                if message:
                    buffer.append(message)

                # We proceed to handle the buffer if
                # 1. it has reached the given size or
                # 2. we drained the queue, but the buffer is smaller than size
                if len(buffer) >= size or (buffer and queue_was_empty):
                    try:
                        with stats.time_block(self.statsd_client):
                            new_messages = self.handle_batch(buffer)

                        stats.mark_successful_job(self.statsd_client)
                        self.post_handle_data()
                    except KeyboardInterrupt as ki:
                        # Raise this for the outer try to handle.
                        raise ki
                    except:
                        logging.exception("Exception handling batch")
                        if self.handle_exception is not None:
                            self.handle_exception()
                        stats.mark_failed_job(self.statsd_client)
                    finally:
                        # If all went well then we have ack'd the messages.
                        # If not, we have requeued or rejected them.
                        # Either way we are done with the buffer.
                        buffer = []

            except KeyboardInterrupt:
                logging.info("Caught Ctrl-C. Byee!")
                break

            except:
                # When could this happen? Perhaps while waiting?
                logging.exception("Exception elsewhere in batched_run_forever")

            else:
                if new_messages:
                    self.queue_new_messages(new_messages)

    def handle_batch(self, messages):
        """Call handle_data on a batch of messages.
        All messages will be ack'd only if the entire function succeeds.
        Otherwise all messages will be rejected/requeued.
        """
        new_messages = []
        try:
            new_messages = self.handle_data([message.payload for message in messages])
            # If we are here, then handle_data ran without any erroes.
            for message in messages:
                message.ack()
        except Exception as e:
            # There was a problem so we reject or requeue the whole batch.
            for message in messages:
                if self.requeue:
                    message.requeue()
                elif self.reject:
                    message.reject()
            # Now that we're done with the messages, handle the exception
            raise e

        return new_messages

    def wait_if_paused(self):
        """Check to see whether the current process should be paused, and
        wait (via time.sleep) until unpaused.
        """
        is_running = True
        while self.is_paused():
            if is_running:
                logging.info("consumer is now paused")
                is_running = False
            # Don't move on until we are unpaused!
            time.sleep(self.pause_delay)

        # Only log this if we came out of the while loop.
        if not is_running:
            logging.info("consumer is not paused")

    def get_full_statsd_prefix(self, base_prefix, queuename):
        """Return a key that is unique to this worker.
        So it will be queue_name.hostname.workerid
        """
        hostname_raw = socket.gethostname()
        # We remove '.' chars from the hostname because statsd uses those to
        # group prefixes.
        hostname = hostname_raw.replace(".", "_")

        # If we have specified a workerid then use it, otherwise use the OS pid
        # (that's bound to be unique per host).
        if self.workerid is not None:
            workerid = self.workerid
        else:
            workerid = str(os.getpid())

        return "{0}.{1}.{2}.{3}".format(base_prefix, queuename, hostname, workerid)
