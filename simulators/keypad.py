
import time
import random

def generate_keypresses():
    keys = ["1", "2", "3", "A", "4", "5", "6", "B", "7", "8", "9", "C", "*", "0", "#", "D"]
    while True:
        # Nasumičan taster koji se pritisne
        key = random.choice(keys)
        yield key

# Funkcija za simulaciju tastature
def run_keyboard_simulator(delay, callback, stop_event, publish_event, settings):
    for key in generate_keypresses():
        time.sleep(delay)  # Delay između pritisaka tastera
        callback(key,stop_event,publish_event, settings,True)
        if stop_event.is_set():
            break