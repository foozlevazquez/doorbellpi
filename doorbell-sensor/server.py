from datetime import datetime, timedelta
from time import sleep, time
import logging
import threading

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


from mq import RabbitMQ

class ThreadSafeDict:

    def __init__(self, **kwargs):
        self.lock = threading.Lock()
        self._data = kwargs or {}

    def set(self, value_dict, blocking=True):
        self.lock.acquire(blocking)
        for k, v in value_dict.items():
            self._data[k] = v
        self.lock.release()

    def inc(self, key, n=1, blocking=True):
        self.lock.acquire(blocking)
        self._data[key] += n
        val = self._data[key]
        self.lock.release()
        return val

    def get(self, blocking=True):
        self.lock.acquire(blocking)
        data = dict(self._data)
        self.lock.release()

        return data


PRESS_COUNT = 'press_count'
PRESS_DT = 'press_dt'
STATE = 'state'

INITIAL_THREAD_SAFE_DATA = {
    PRESS_COUNT: 0,
    PRESS_DT: None,

    # Set later
    STATE: None,
}


thread_safe_data = ThreadSafeDict(**INITIAL_THREAD_SAFE_DATA)


def set_press_dt(dt=None):
    dt = dt or datetime.utcnow()
    assert isinstance(dt, datetime)
    logging.debug("Setting press dt: %s", str(dt))
    thread_safe_data.set({PRESS_DT: dt})


def get_press_dt():
    return thread_safe_data.get()[PRESS_DT]


def inc_press_count(n=1):
    return thread_safe_data.inc(PRESS_COUNT, n)


def get_press_count():
    return thread_safe_data.get()[PRESS_COUNT]


def set_state(state):
    old_state = thread_safe_data.get()[STATE]
    logging.debug("setting state from %s to %s: ",
                  old_state and old_state.__name__,
                  state.__name__)

    state.enter()

    thread_safe_data.set({STATE: state})
    if old_state:
        old_state.exit()


def get_state():
    return thread_safe_data.get()[STATE]


WHITE = 'white'
RED = 'red'
GREEN = 'green'

LED_PINS = {
    WHITE: 8,
    RED: 16,
    GREEN: 18,
}

BUTTON_PIN = 10

class Hardware:

    @classmethod
    def turn_on(cls, color):
        assert color in LED_PINS
        logging.debug("Turning ON pin %d (%s)", LED_PINS[color], color)
        GPIO.output(LED_PINS[color], GPIO.HIGH)

    @classmethod
    def turn_off(cls, color):
        assert color in LED_PINS
        logging.debug("Turning OFF pin %d (%s)", LED_PINS[color], color)
        GPIO.output(LED_PINS[color], GPIO.LOW)

    @classmethod
    def setup(cls):

        logging.basicConfig(format='%(asctime)s[%(levelname)s]:%(message)s',
                            level=logging.DEBUG)
        # Ignore warning for now
        GPIO.setwarnings(False)

        # Use physical pin numbering
        GPIO.setmode(GPIO.BOARD)

        for _, pin in LED_PINS.items():
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        for color in LED_PINS:
            cls.turn_on(color)
            sleep(1)
            cls.turn_off(color)

        # Set pin BUTTON_PIN to be an input pin and set initial value to be
        # pulled high (on).  Button will short line.
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Setup event on pin BUTTON_PIN falling edge
        # NB: The polling for the GPIO event is done in a separate thread (a
        # pthread), which is created when this is run.
        GPIO.add_event_detect(BUTTON_PIN,
                              GPIO.FALLING,
                              callback=cls.button_callback,
                              bouncetime=300)

    ## NB: This runs in a pthread alongside. See GPIO.add_event_detect above.
    @classmethod
    def button_callback(cls, channel):
        get_state().button_callback(channel)


# Wait: waiting for button
# Acknowledge: acknowledging press
# Busy: busy

class State:

    @classmethod
    def button_callback(cls, channel):
        logging.info("Button pressed")

    @classmethod
    def update(cls, ms_since_last):
        raise NotImplementedError

    @classmethod
    def enter(cls):
        raise NotImplementedError

    @classmethod
    def exit(cls):
        raise NotImplementedError


class WaitState(State):

    @classmethod
    def enter(cls):
        Hardware.turn_on(WHITE)

    @classmethod
    def exit(cls):
        Hardware.turn_off(WHITE)

    @classmethod
    def update(cls, ms_since_last):
        pass
        # button_callback does the work
        # Could insert transition random lightshow here

    @classmethod
    def button_callback(cls, channel):
        super().button_callback(channel)

        RabbitMQ.publish("2215NNorris:front_doorbell:pressed")
        set_press_dt()
        inc_press_count()
        set_state(AcknowledgeStateOn)


class AcknowledgeState(State):

    iteration = 0

    @classmethod
    def enter(cls):
        pass

    @classmethod
    def exit(cls):
        pass

    @classmethod
    def button_callback(cls, channel):
        super().button_callback(channel)

    @classmethod
    def update(cls, ms_since_last):
        cls.iteration += 1

        if (datetime.utcnow() - get_press_dt()) > timedelta(seconds=10):
            set_state(WaitState)

class AcknowledgeStateOn(AcknowledgeState):

    @classmethod
    def update(cls, ms_since_last):
        super().update(ms_since_last)

        if (cls.iteration % 50) == 0:
            Hardware.turn_on('green')
            set_state(AcknowledgeStateOff)


class AcknowledgeStateOff(AcknowledgeState):

    @classmethod
    def update(cls, ms_since_last):
        super().update(ms_since_last)

        if (cls.iteration % 50) == 0:
            Hardware.turn_off('green')
            set_state(AcknowledgeStateOn)



if __name__ == '__main__':
    try:
        RabbitMQ.init_publisher()
        RabbitMQ.publish("2215NNorris:front_doorbell:program_start")

        Hardware.setup()
        set_state(WaitState)
        last_time_run = time()
        top_level_iter = 0

        while True:
            now = time()
            get_state().update(now - last_time_run)
            last_time_run = now
            sleep(.010)
            top_level_iter += 1

            if (top_level_iter % 100) == 0:
                logging.debug("iteration %s", top_level_iter)

    except KeyboardInterrupt:
            pass


    GPIO.cleanup() # Clean up
