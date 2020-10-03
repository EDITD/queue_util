try:
    import mock
except ImportError:
    from unittest import mock
import unittest

from queue_util.consumer import Consumer


class TestConsumer(unittest.TestCase):
    @mock.patch('kombu.BrokerConnection', autospec=True)
    @mock.patch('statsd.StatsClient', autospec=True)
    @mock.patch.object(Consumer, 'post_handle_data')
    @mock.patch('logging.exception')
    def test_consumer(self, mock_logging_exception, mock_post_handle_data,
                      mock_statsd, mock_broker_connection):
        """A handle_data generator function"""

        # Handler that yields messages the first time it is called and then
        # raises a KeyboardInterrupt on subsequent calls.
        class HandleData(object):
            CALL_COUNT = 0

            def handle_data(self, payload):
                self.CALL_COUNT += 1
                if 1 == self.CALL_COUNT:
                    yield 'dest_queue', 'payload1'
                    yield 'dest_queue', 'payload2'
                    yield 'dest_queue', 'payload3'
                else:
                    raise KeyboardInterrupt

        handle_exception = mock.Mock()
        c = Consumer(
            'source_queue', HandleData().handle_data,
            rabbitmq_host='host',
            handle_exception=handle_exception,
            statsd_host='stats',
        )
        c.run_forever()

        # Connection was created
        mock_broker_connection.assert_called_once_with('host')

        # Message were fetched from source
        source = c.get_queue('source_queue')
        expected = [
            mock.call(block=True, timeout=None),
            mock.call().ack(),
            mock.call(block=True, timeout=None),
        ]
        source.get.assert_has_calls(expected)

        # Three messages were sent to destination
        dest = c.get_queue('dest_queue')
        expected = [
            mock.call('payload1'),
            mock.call('payload2'),
            mock.call('payload3'),
        ]
        dest.put.assert_has_calls(expected)

        # Post-handle was called
        mock_post_handle_data.assert_called_once_with()

        # Job was marked as successful
        c.statsd_client.incr.assert_called_once_with('success')

        # Exception handler was not called
        handle_exception.assert_not_called()

        # Exception was not logged
        mock_logging_exception.assert_not_called()

        # Messages were acked and not requeued or rejected
        mock_message = source.get()
        self.assertEqual(1, mock_message.ack.call_count)
        mock_message.requeue.assert_not_called()
        mock_message.reject.assert_not_called()

    @mock.patch('kombu.BrokerConnection', autospec=True)
    @mock.patch('statsd.StatsClient', autospec=True)
    @mock.patch.object(Consumer, 'post_handle_data')
    @mock.patch('logging.exception')
    def test_retry_failures(self, mock_logging_exception, mock_post_handle_data,
                            mock_statsd, mock_broker_connection):
        """Failed messages are retried"""
        # Handler that raises a ValueError the first time it is called and then
        # raises a KeyboardInterrupt on subsequent calls.
        class HandleData(object):
            CALL_COUNT = 0

            def handle_data(self, payload):
                self.CALL_COUNT += 1
                if 1 == self.CALL_COUNT:
                    raise ValueError('Something bad')
                else:
                    raise KeyboardInterrupt

        handle_exception = mock.Mock()
        c = Consumer(
            'source_queue', HandleData().handle_data,
            rabbitmq_host='host',
            handle_exception=handle_exception,
            statsd_host='stats',
            dont_requeue=False,
            reject=False,
        )
        c.run_forever()

        # Post-handle was not called
        mock_post_handle_data.assert_not_called()

        # Job was not marked as successful
        c.statsd_client.incr.assert_called_once_with('failure')

        # Exception handler was not called
        handle_exception.assert_called_once_with()

        # Exception was logged
        mock_logging_exception.assert_called_once()

        # Messages were requeued and not acked or rejected
        source = c.get_queue('source_queue')
        mock_message = source.get()
        mock_message.ack.assert_not_called()
        self.assertEqual(1, mock_message.requeue.call_count)
        mock_message.reject.assert_not_called()

    @mock.patch('kombu.BrokerConnection', autospec=True)
    def test_reject_failures(self, mock_broker_connection):
        """Failed messages are rejected"""
        # Handler that raises a ValueError the first time it is called and then
        # raises a KeyboardInterrupt on subsequent calls.
        class HandleData(object):
            CALL_COUNT = 0

            def handle_data(self, payload):
                self.CALL_COUNT += 1
                if 1 == self.CALL_COUNT:
                    raise ValueError('Something bad')
                else:
                    raise KeyboardInterrupt

        c = Consumer(
            'source_queue', HandleData().handle_data,
            rabbitmq_host='host',
            dont_requeue=True,
            reject=True,
        )
        c.run_forever()

        # Messages were rejected and not acked or requeued
        source = c.get_queue('source_queue')
        mock_message = source.get()
        mock_message.ack.assert_not_called()
        mock_message.requeue.assert_not_called()
        self.assertEqual(1, mock_message.reject.call_count)

    @mock.patch('kombu.BrokerConnection', autospec=True)
    @mock.patch('statsd.StatsClient', autospec=True)
    @mock.patch.object(Consumer, 'post_handle_data')
    @mock.patch('logging.exception')
    def test_consumer_batch(self, mock_logging_exception, mock_post_handle_data,
                            mock_statsd, mock_broker_connection):
        """A handle_data generator function"""

        # Handler that yields messages the first time it is called and then
        # raises a KeyboardInterrupt on subsequent calls.
        class HandleData(object):
            CALL_COUNT = 0

            def handle_data(self, payloads):
                self.CALL_COUNT += 1
                if 1 == self.CALL_COUNT:
                    for payload in payloads:
                        yield 'dest_queue', payload
                else:
                    raise KeyboardInterrupt

        handle_exception = mock.Mock()
        c = Consumer(
            'source_queue', HandleData().handle_data,
            rabbitmq_host='host',
            handle_exception=handle_exception,
            statsd_host='stats',
        )
        c.batched_run_forever(size=10)

        # Connection was created
        mock_broker_connection.assert_called_once_with('host')

        # 20 message fetched - handled as two batches of 10 messages
        source = c.get_queue('source_queue')
        self.assertEqual(20, source.get.call_count)

        dest = c.get_queue('dest_queue')
        self.assertEqual(10, dest.put.call_count)

        # Post-handle was called
        mock_post_handle_data.assert_called_once_with()

        # Job was marked as successful
        c.statsd_client.incr.assert_called_once_with('success')

        # Exception handler was not called
        handle_exception.assert_not_called()

        # Exception was not logged
        mock_logging_exception.assert_not_called()

        # Messages were acked and not requeued or rejected
        mock_message = source.get()
        self.assertEqual(10, mock_message.ack.call_count)
        mock_message.requeue.assert_not_called()
        mock_message.reject.assert_not_called()

    @mock.patch('kombu.BrokerConnection', autospec=True)
    @mock.patch('statsd.StatsClient', autospec=True)
    @mock.patch.object(Consumer, 'post_handle_data')
    @mock.patch('logging.exception')
    def test_batch_retry_failures(self, mock_logging_exception, mock_post_handle_data,
                                  mock_statsd, mock_broker_connection):
        """Batches of failed messages are retried"""
        # Handler that raises a ValueError the first time it is called and then
        # raises a KeyboardInterrupt on subsequent calls.
        class HandleData(object):
            CALL_COUNT = 0

            def handle_data(self, payload):
                self.CALL_COUNT += 1
                if 1 == self.CALL_COUNT:
                    raise ValueError('Something bad')
                else:
                    raise KeyboardInterrupt

        handle_exception = mock.Mock()
        c = Consumer(
            'source_queue', HandleData().handle_data,
            rabbitmq_host='host',
            handle_exception=handle_exception,
            statsd_host='stats',
            dont_requeue=False,
            reject=False,
        )
        c.batched_run_forever(size=10)

        # Post-handle was not called
        mock_post_handle_data.assert_not_called()

        # Job was not marked as successful
        c.statsd_client.incr.assert_called_once_with('failure')

        # Exception handler was not called
        handle_exception.assert_called_once_with()

        # Exception was logged
        mock_logging_exception.assert_called_once()

        # Messages were requeued and not acked or rejected
        source = c.get_queue('source_queue')
        mock_message = source.get()
        mock_message.ack.assert_not_called()
        self.assertEqual(10, mock_message.requeue.call_count)
        mock_message.reject.assert_not_called()

    @mock.patch('kombu.BrokerConnection', autospec=True)
    def test_batch_reject_failures(self, mock_broker_connection):
        """Failed messages are rejected"""
        # Handler that raises a ValueError the first time it is called and then
        # raises a KeyboardInterrupt on subsequent calls.
        class HandleData(object):
            CALL_COUNT = 0

            def handle_data(self, payload):
                self.CALL_COUNT += 1
                if 1 == self.CALL_COUNT:
                    raise ValueError('Something bad')
                else:
                    raise KeyboardInterrupt

        c = Consumer(
            'source_queue', HandleData().handle_data,
            rabbitmq_host='host',
            dont_requeue=True,
            reject=True,
        )
        c.batched_run_forever(size=10)

        # Messages were rejected and not acked or requeued
        source = c.get_queue('source_queue')
        mock_message = source.get()
        mock_message.ack.assert_not_called()
        mock_message.requeue.assert_not_called()
        self.assertEqual(10, mock_message.reject.call_count)


if '__main__' == __name__:
    unittest.main()
