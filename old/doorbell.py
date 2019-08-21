from datetime import datetime, timedelta
from time import sleep

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library


class DoorBellProgram:
    LED_PINS = {
        'white': 8,
        'red': 16,
        'green': 18,
    }

    BUTTON_PIN = 10
    button_press = None
    press_timeout = timedelta(seconds=1)
    loop_sleep_ms = 100

    @classmethod
    def setup(cls):
        # Ignore warning for now
        GPIO.setwarnings(False)

        # Use physical pin numbering
        GPIO.setmode(GPIO.BOARD)

        for _, pin in LED_PINS.items():
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

        # Set pin BUTTON_PIN to be an input pin and set initial value to be pulled high (on)
        # button will short line.
        GPIO.setup(cls.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Setup event on pin BUTTON_PIN falling edge
        GPIO.add_event_detect(cls.BUTTON_PIN,
                              GPIO.FALLING,
                              callback=cls.button_callback)

    @classmethod
    def button_callback(cls, channel):
        if not cls.button_press:
            print("Button pressed")
            cls.button_press = datetime.utcnow()

    @classmethod
    def run(cls):
        while True:
            sleep(1000.0 * cls.loop_sleep_ms)
            if cls.button_press:
                if (datetime.utcnow() - cls.button_press) < cls.press_timeout:
                    GPIO.output(cls.RED_LED_PIN, GPIO.HIGH) # Turn on
                else:
                    cls.button_press = None
                    GPIO.output(cls.RED_LED_PIN, GPIO.LOW) # Turn off


if __name__ == '__main__':
    DoorBellProgram.setup()
    try:
        DoorBellProgram.run()
    except KeyboardInterrupt:
        pass

    GPIO.cleanup() # Clean up
