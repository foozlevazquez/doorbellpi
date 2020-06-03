import os
from datetime import datetime, timedelta
import time
import logging
import threading
import subprocess

import requests

os.sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '../lib/py'))

from doorbell_mqtt import MQTT

def handle_message(s):
    print(" received: {}".format(s))
    if 'pressed' in s:
        logging.info("Playing...")
        subprocess.run(["/usr/bin/aplay", "/home/pi/ChurchTowerClock.wav"])

        # Save front door image
        # dstr = str(datetime.utcnow()).replace(' ', '_')
        # r = requests.get('http://192.168.110.34/image/jpeg.cgi')
        # with open('/opt/doorbell_pics/{}.jpg'.format(dstr), 'wb') as f:
        #     f.write(r.content)

def main():
    logging.basicConfig(format='%(asctime)s[%(levelname)s]:%(message)s',
                        level=logging.DEBUG)

    logging.info("Starting...")

    started = False
    while not started:
        try:
            MQTT.init_subscriber(callback_fn=handle_message)
            started = True
            logging.info("...waiting for messages...")
        except ConnectionRefusedError:
            logging.warning("waiting for MQTT, sleeping...")
            time.sleep(5)

    MQTT.check(block=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
            pass
