import os
from datetime import datetime, timedelta
from time import sleep, time
import logging
import threading
import subprocess

import requests

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


os.sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '../lib/py'))

from mq import RabbitMQ


def handle_message(ch, method, properties, body):
    print(" received: {}".format(body))

    if 'pressed' in body.decode('utf-8'):
        logging.info("Playing...")
        subprocess.run(["/usr/bin/aplay", "/home/pi/ChurchTowerClock.wav"])

        # Save front door image
        dstr = str(datetime.utcnow()).replace(' ', '_')
        r = requests.get('http://192.168.110.34/image/jpeg.cgi')
        with open('/opt/doorbell_pics/{}.jpg'.format(dstr), 'wb') as f:
            f.write(r.content)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s[%(levelname)s]:%(message)s',
                        level=logging.DEBUG)

    try:
        logging.info("Starting, waiting for messages...")
        RabbitMQ.init_subscriber(callback_fn=handle_message)
    except KeyboardInterrupt:
            pass
