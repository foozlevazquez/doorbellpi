# doorbellpi

pi@doorbellringerpi.fooz.lan 192.168.110.68

### PI: Install
- sudo apt-get install mosquitto mosquitto-clients

- test:

```
mosquitto_sub -d -t mytopic &
mosquitto_sub -d -t mytopic -m MyMessage

```


### Py Lib

```bash
pip3 install paho-mqtt
python3 -i

```

```python
import paho.mqtt.client as mqtt

c = mqtt.Client()

c.connect('192.168.110.65')


## publisher
c.publish('topic', 'message')


## subscriber

def handle_message(client, userdata, message):
    print("Got: userdata: {}, message: {}".format(userdata, message))

c.on_message = handle_message

c.subscribe('topic')
```
