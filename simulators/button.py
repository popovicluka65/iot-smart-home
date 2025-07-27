import time
import random

def generate_values(delay, stop_event):
    value = 0
    previous_value = None
    while True:
        time.sleep(delay)
        value = random.randint(0,1) == 1
        if value != previous_value:
            previous_value = value
            yield value
        else:
            continue
        if stop_event.is_set():
            break


def run_button_simulator(delay, callback, stop_event, publish_event, settings, threshold=0.6):
    for value in generate_values(delay=10, stop_event=stop_event):
        # print(value)
        callback( value == 1,publish_event, settings)
        if stop_event.is_set():
            break