import contextlib
import time


@contextlib.contextmanager
def time_block(statsd_client):
    if statsd_client:
        start = time.time()
        yield
        end = time.time()

        delta_in_ms = int((end - start) * 1000)
        statsd_client.timing("job_time", delta_in_ms)
    else:
        # Do nothing here.
        yield


def mark_successful_job(statsd_client):
    if not statsd_client:
        return
    statsd_client.incr("success")


def mark_failed_job(statsd_client):
    if not statsd_client:
        return
    statsd_client.incr("failure")
