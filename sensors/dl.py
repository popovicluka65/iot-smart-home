import RPi.GPIO as GPIO
import time

class DL(object):
    def __init__(self,name, pin):
        self.name = name
        self.pin = pin


def run_dl_loop(pin, callback, stop_event, event_on, event_off, settings,publish_event):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)

    try:
        while not stop_event.is_set():
            # Paljenje LED-a
            if event_on.wait(timeout=0.1):  # Čekaj na signal
                GPIO.output(pin, GPIO.HIGH)
                callback(True, settings,publish_event)
                event_on.clear()

            # Gašenje LED-a
            if event_off.wait(timeout=0.1):
                GPIO.output(pin, GPIO.LOW)
                callback(False, settings,publish_event)
                event_off.clear()
    finally:
        GPIO.cleanup(pin)  # Očisti GPIO na kraju rada