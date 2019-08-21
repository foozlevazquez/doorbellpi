import os
from datetime import datetime
import time

import pika

EXCHANGE_NAME = 'doorbellexch'

class RabbitMQ:

    connection = None
    channel = None
    queue_name = None

    @classmethod
    def _init(cls):
        # Parse CLODUAMQP_URL (fallback to localhost)
        url = os.environ.get('CLOUDAMQP_URL',
                             'amqp://mq:foobarbaz5501@192.168.110.10/')

        params = pika.URLParameters(url)
        params.socket_timeout = None
        cls.connection = pika.BlockingConnection(params) # Connect to CloudAMQP
        cls.channel = cls.connection.channel() # start a channel
        cls.channel.exchange_declare(exchange=EXCHANGE_NAME,
                                     exchange_type='fanout')

    @classmethod
    def init_publisher(cls):
        cls._init()

    @classmethod
    def publish(cls, message):
        cls.channel.basic_publish(exchange=EXCHANGE_NAME, routing_key='',
                                  body=message)

    @classmethod
    def init_subscriber(cls, callback_fn=None):
        assert callback_fn

        cls._init()
        cls.queue_name = cls.channel.queue_declare(queue='', exclusive=True
        ).method.queue
        cls.channel.queue_bind(exchange=EXCHANGE_NAME, queue=cls.queue_name)
        cls.channel.basic_consume(queue=cls.queue_name,
                                  on_message_callback=callback_fn)
        cls.channel.start_consuming()


def do_subscriber():
    def cb(ch, method, properties, body):
        print(" received: {}".format(body))

    RabbitMQ.init_subscriber(callback_fn=cb)


def do_publisher():
    RabbitMQ.init_publisher()

    count = 0

    while True:
        RabbitMQ.publish("{}: {}".format(count, str(datetime.utcnow())))
        count += 1
        time.sleep(1)


if __name__ == "__main__":

    if len(os.sys.argv) < 2:
        print("Usage: {} [subscribe|publish]".format(
            os.sys.argv[0]))
        os.sys.exit(1)

    if os.sys.argv[1] == "subscribe":
        do_subscriber()
    elif os.sys.argv[1] == "publish":
        do_publisher()
