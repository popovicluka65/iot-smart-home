from simulators.uds import run_uds_simulator
import threading
import time
from locks import print_lock
import paho.mqtt.publish as publish
import json

uds_batch = []
publish_data_counter = 0
publish_data_limit = 3
counter_lock = threading.Lock()

def publisher_task(event, uds_batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_dht_batch = uds_batch.copy()
            publish_data_counter = 0
            uds_batch.clear()
        try:
            publish.multiple(local_dht_batch, hostname="localhost", port=1883)
            print(f'Published {publish_data_limit} uds values')
        except:
            print("greska")
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, uds_batch,))
publisher_thread.daemon = True
publisher_thread.start()

#KOPIRANO SA dht componente i prepravljeno za uds
def uds_callback(distance, publish_event, settings,verbose = True):
    global publish_data_counter, publish_data_limit
    t = time.localtime()
    print(settings)
    if verbose:
        with print_lock:
            print("="*20)
            print(f"Timestamp: {time.strftime('%H:%M:%S', t)}")
            if distance:
                print(f"Distance: {distance}m")
            else:
                 print(f"No distance")
            print(f"Name: {settings['name']}")

    distance_payload = {
        "measurement": "distance",
        "simulated": settings['simulated'],
        "runs_on": settings["runs_on"],
        "name": settings["name"],
        "value": distance,
        "field": settings["influxdb_field"],
        "bucket": settings["influxdb_bucket"],
        "front": False
    }

    with counter_lock:
        if publish_data_counter == publish_data_limit - 1:
            distance_payload["front"] = True
        uds_batch.append(('topic/distance', json.dumps(distance_payload), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
         publish_event.set()
    #publish_event.set()


def run_uds(settings, threads, stop_event):
        if settings['simulated']:
            with print_lock:
                print("Starting uds sumilator which name is:" + settings["name"])
            uds_thread = threading.Thread(target = run_uds_simulator, args=(1, uds_callback, stop_event, publish_event,settings))
            uds_thread.start()
            threads.append(uds_thread)
            with print_lock:
                print("UDS sumilator started which name is:" + settings["name"])
        else:
            from sensors.uds import run_uds_loop, UDS
            with print_lock:
                print("Starting uds loop which name is "+ settings["name"])
            #pokupimo iz konfiguracije
            uds = UDS(settings["name"],settings["trig_pin"],settings["echo_pin"])
            uds_thread = threading.Thread(target = run_uds_simulator, args=(uds,2, uds_callback, stop_event, publish_event,settings))
            uds_thread.start()
            threads.append(uds_thread)
            with print_lock:
                print("UDS sensor started which name is:" + settings["name"])