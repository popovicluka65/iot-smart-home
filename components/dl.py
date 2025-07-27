from simulators.dl import run_dl_simulator
import threading
import time
from locks import print_lock
import paho.mqtt.publish as publish
import json

dl_batch = []
publish_data_counter = 0
publish_data_limit = 2
counter_lock = threading.Lock()

def publisher_task(event, dl_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_dl_batch = dl_batch.copy()
            publish_data_counter = 0
            dl_batch.clear()
        try:
            publish.multiple(local_dl_batch, hostname="localhost", port=1883)
            print(f'Published {publish_data_limit} door light values')
        except:
            print("greska")
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, dl_batch,))
publisher_thread.daemon = True
publisher_thread.start()

def dl_callback(status, settings, publish_event,verbose = True):
    global publish_data_counter, publish_data_limit
    t = time.localtime()
    with print_lock:
        print("=" * 20)
        print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
        print(f"Status: {'ON' if status else 'OFF'}")
        print(f"LED Name: {settings['name']}")

    dl_payload = {
        "measurement": "dl",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
        "value": status,
        "field": settings["influxdb_field"],
        "bucket": settings["influxdb_bucket"],
        "front":True
    }

    with counter_lock:
        if publish_data_counter == publish_data_limit - 1:
            dl_payload["front"] = True
        dl_batch.append(('topic/dl', json.dumps(dl_payload), 0, False))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()
        


def run_dl(settings, threads, stop_event, motion_detected_event=None):
    """
    Funkcija za pokretanje LED-a (simuliranog ili stvarnog).
    :param settings: Podešavanja za LED.
    :param threads: Lista thread-ova za upravljanje.
    :param stop_event: Event za zaustavljanje rada.
    :param event_on: Event koji pali LED.
    :param event_off: Event koji gasi LED.
    """

    #print("UDJE U LED")
    if settings['simulated']:
        with print_lock:
            print(f"Starting LED simulator which name is: {settings['name']}")
        led_thread = threading.Thread(target=run_dl_simulator, args=(dl_callback, stop_event, publish_event, settings, motion_detected_event))
        led_thread.start()
        threads.append(led_thread)
        with print_lock:
            print(f"LED simulator started which name is: {settings['name']}")
    else:
        from sensors.dl import run_dl_loop,DL
        with print_lock:
            print(f"Starting LED loop which name is: {settings['name']}")
        dl = DL(settings['name'],settings['pin'])
        led_thread = threading.Thread(target=run_dl_loop, args=(dl, dl_callback, stop_event, publish_event, settings, motion_detected_event))
        led_thread.start()
        threads.append(led_thread)
        with print_lock:
            print(f"LED loop started which name is: {settings['name']}")
