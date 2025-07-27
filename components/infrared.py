import json
import threading
import time
from paho.mqtt import publish

from simulators.infrared import run_infrared_simulator
from locks import print_lock

infrared_batch = []
publish_data_counter = 0
publish_data_limit = 1
counter_lock = threading.Lock()


def publisher_task(event, infrared_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_infrared_batch = infrared_batch.copy()
            publish_data_counter = 0
            infrared_batch.clear()
        publish.multiple(local_infrared_batch, hostname="localhost", port=1883)
        print(f'Published {publish_data_limit} infrared values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, infrared_batch,))
publisher_thread.daemon = True
publisher_thread.start()


def infrared_callback(key, publish_event,settings, verbose=True):
    global publish_data_counter, publish_data_limit

    t = time.localtime()
    if verbose:
        with print_lock:
            print("=" * 20)
            print(settings["name"] )
            print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
            print(f"Key pressed: {key}")

    payload = {
        "measurement": "Infrared",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
        "value": key,
        "field": settings["influxdb_field"],
        "bucket": settings["influxdb_bucket"],
        "datetime": time.strftime('%d.%m.%Y. %H:%M:%S', t),
        "front": False
    }

    with counter_lock:
        infrared_batch.append(('topic/infrared', json.dumps(payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()


def run_infrared(settings, threads, stop_event,bir_rgb_event,bir_rgb_mappings,queue):
    if settings['simulated']:
        print("Starting {} simulator".format(settings["name"]))
        ir_thread = threading.Thread(target=run_infrared_simulator,
                                      args=(3, infrared_callback, stop_event, publish_event, settings,bir_rgb_event,bir_rgb_mappings,queue))
        ir_thread.start()
        threads.append(ir_thread)
        print("{0} simulator started".format(settings["name"]))
    else:
        from sensors.infrared import run_ir_loop, Infrared
        print("Starting {} loop".format(settings["name"]))
        ir = Infrared(settings["pin"], settings["name"])
        ir_thread = threading.Thread(target=run_ir_loop,
                                      args=(ir, 10, infrared_callback, stop_event, publish_event, settings))
        ir_thread.start()
        threads.append(ir_thread)
        print("{} loop started".format(settings["name"]))