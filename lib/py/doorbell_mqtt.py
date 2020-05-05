import os
from datetime import datetime
import time

import paho.mqtt.client as mqtt

TOPIC_NAME = 'doorbell'

class MQTT:

    client = mqtt.Client()

    @classmethod
    def _init(cls):
        cls.client.connect(
            os.environ.get('MQTT_HOST') or '192.168.110.65')

    @classmethod
    def init_publisher(cls):
        cls._init()

    @classmethod
    def publish(cls, message):
        cls._init()
        cls.client.publish(TOPIC_NAME, message)

    @classmethod
    def init_subscriber(cls, callback_fn=None):
        assert callback_fn

        cls._init()
        cls.client.on_message = callback_fn
        cls.client.subscribe(TOPIC_NAME)

    @classmethod
    def check(cls, block=False):
        # Does one check, then returns
        if block:
            cls.client.loop_forever()
        else:
            cls.client.loop()


################################################################
# Test code
################################################################
def do_subscriber(blocking=False):
    done = False

    def _on_message(client, userdata, message):
        s = message.payload.decode('utf-8')
        print(" received: {}".format(s))
        if message == 'QUIT':
            done = True

    MQTT.init_subscriber(_on_message)

    if blocking:
        MQTT.check(block=True)
    else:
        while (not done):
            MQTT.check()
            time.sleep(0.1)


def do_publisher():

    count = 0
    while True:
        s = "{}: {}".format(count, str(datetime.utcnow()))
        print("Publishing: ", s)
        MQTT.publish(s)
        count += 1
        time.sleep(1)


if __name__ == "__main__":

    if len(os.sys.argv) < 2:
        print("Usage: {} [subscribe|publish]".format(
            os.sys.argv[0]))
        os.sys.exit(1)

    if os.sys.argv[1] == "subscribe":
        do_subscriber(blocking=(len(os.sys.argv) > 2))
    elif os.sys.argv[1] == "publish":
        do_publisher()
