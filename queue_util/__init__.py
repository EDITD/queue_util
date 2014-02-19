from queue_util.consumer import Consumer
from queue_util.producer import Producer

import json

import requests


def get_num_messages(rabbitmq_host, queue_name, port=15672, vhost="%2F", auth=None):
    """A (very!) approximate attempt to get the number of messages in a queue.
    It uses the rabbitmq http API (so make sure that is installed).
    """
    if not auth:
        auth = ("guest", "guest")
    url = "http://{0}:{1}/api/queues/{2}/{3}".format(rabbitmq_host, port, vhost, queue_name)

    response = requests.get(url, auth=auth)
    
    queue_data = json.loads(response.content)
    return queue_data["messages"]
