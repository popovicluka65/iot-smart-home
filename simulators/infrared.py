import time
import random

def generate_keypress():
    keys = ["LEFT", "RIGHT", "UP", "DOWN",       
            "2", "3", "1", "OK", "4", "5", "6", "7", "8", "9", "*", "0", "#"]
    key = random.choice(keys)
    return key

# Funkcija za simulaciju tastature, copy paste je od tastature
def run_infrared_simulator(delay, callback, stop_event, publish_event, settings,bir_rgb_event,bir_rgb_mappings,queue):
    while True:
        key = generate_keypress()
        if key in bir_rgb_mappings:
            queue.put(bir_rgb_mappings[key])
            bir_rgb_event.set()
        
        callback(key, publish_event, settings,True)
        if stop_event.is_set():
            break
        time.sleep(delay)