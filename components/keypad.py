from simulators.keypad import run_keyboard_simulator
import threading
import time
from locks import print_lock
from paho.mqtt import publish
import json

ms_batch = []
publish_data_counter = 0
publish_data_limit = 2
counter_lock = threading.Lock()

key_to_number = {
    "1": 1, "2": 2, "3": 3, "A": 10,
    "4": 4, "5": 5, "6": 6, "B": 11,
    "7": 7, "8": 8, "9": 9, "C": 12,
    "*": 13, "0": 0, "#": 14, "D": 15
}

def publisher_task(event, ms_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_ms_batch = ms_batch.copy()
            publish_data_counter = 0
            ms_batch.clear()
        publish.multiple( local_ms_batch , hostname="localhost", port=1883)
        print(f'Published {publish_data_limit} ms values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, ms_batch,))
publisher_thread.daemon = True
publisher_thread.start()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, ms_batch,))
publisher_thread.daemon = True
publisher_thread.start()



def keyboard_callback(key,stop_event, publish_event, settings, verbose=True):
    global publish_data_counter, publish_data_limit
    if verbose:
        t = time.localtime()
        with print_lock:
            print("="*20)
            print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
            print(f"Key Pressed: {key}")
            print(f"Keyboard Simulator Name: {settings['name']}")

    keypad_payload = {
        "measurement": "key",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
        "value": key,
        "field": settings["influxdb_field"],
        "bucket": settings["influxdb_bucket"],
        "front":False
    }

    with counter_lock:
        if publish_data_counter == publish_data_limit - 1:
            keypad_payload["front"] = True
        ms_batch.append(('topic/keypad', json.dumps(keypad_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()

# Funkcija koja pokreće tastaturu, i stvarnu i simuliranu
def run_keyboard(settings, threads, stop_event):
    if settings['simulated']:
        with print_lock:
            print(f"Starting keyboard simulator with name: {settings['name']}")
        keyboard_thread = threading.Thread(target=run_keyboard_simulator, args=(2, keyboard_callback, stop_event,publish_event, settings))
        keyboard_thread.start()
        threads.append(keyboard_thread)
        with print_lock:
            print(f"Keyboard simulator started with name: {settings['name']}")
    else:
        from sensors.keypad import Keyboard,run_keyboard_loop
        with print_lock:
            print("Starting keypad loop which name is "+ settings["name"])
        keyboard = Keyboard(settings)
        kb_thread = threading.Thread(target=run_keyboard_loop, args=(keyboard, 2, keyboard_callback, stop_event,publish_event,settings))
        kb_thread.start()
        threads.append(kb_thread)
        with print_lock:
            print("Keyboard loop started which name is "+ settings["name"])

    