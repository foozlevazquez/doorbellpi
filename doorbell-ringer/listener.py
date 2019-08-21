from datetime import datetime, timedelta
from time import sleep, time
import logging
import threading
import subprocess

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


from mq import RabbitMQ



def handle_message(ch, method, properties, body):
    print(" received: {}".format(body))
    if 'pressed' in body.decode('utf-8'):
        logging.info("Playing...")
        subprocess.run(["/usr/bin/aplay", "/home/pi/ChurchTowerClock.wav"])


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s[%(levelname)s]:%(message)s',
                        level=logging.DEBUG)

    try:
        logging.info("Starting, waiting for messages...")
        RabbitMQ.init_subscriber(callback_fn=handle_message)
    except KeyboardInterrupt:
            pass
